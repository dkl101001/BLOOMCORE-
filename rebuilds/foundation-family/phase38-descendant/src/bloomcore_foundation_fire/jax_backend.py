# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from typing import NamedTuple

import jax
import jax.numpy as jnp

from .model import FireConfig, FireMetrics


class JaxState(NamedTuple):
    tick: jax.Array
    vector: jax.Array
    previous: jax.Array
    identity: jax.Array
    field: jax.Array
    memory: jax.Array
    hdot_history: jax.Array
    energy_prev: jax.Array
    topology: jax.Array
    coupling: jax.Array
    key: jax.Array


def initial_jax_state(*, vector, field, topology=None, seed: int = 151) -> JaxState:
    vector32 = jnp.asarray(vector, dtype=jnp.float32)
    field32 = jnp.asarray(field, dtype=jnp.float32)
    n = vector32.shape[0]
    topology32 = (
        jnp.eye(n, dtype=jnp.float32)
        if topology is None
        else jnp.asarray(topology, dtype=jnp.float32)
    )
    # Match the NumPy reference and keep energy invariant under zero padding.
    energy = jnp.mean(field32 * field32) + 0.5 * jnp.sum(vector32 * vector32)
    return JaxState(
        tick=jnp.asarray(0, dtype=jnp.int32),
        vector=vector32,
        previous=vector32,
        identity=vector32,
        field=field32,
        memory=vector32,
        hdot_history=jnp.zeros(4, dtype=jnp.float32),
        energy_prev=energy,
        topology=topology32,
        coupling=jnp.ones_like(vector32),
        key=jax.random.key(seed),
    )


def _kgrid(shape, half_extent):
    height, width = shape
    dx = (2.0 * half_extent) / width
    kx = 2.0 * jnp.pi * jnp.fft.fftfreq(width, d=dx)
    ky = 2.0 * jnp.pi * jnp.fft.fftfreq(height, d=dx)
    grid_x, grid_y = jnp.meshgrid(kx, ky, indexing="xy")
    return grid_x, grid_y, grid_x * grid_x + grid_y * grid_y


def _field_step(field, cfg: FireConfig):
    grid_x, grid_y, grid2 = _kgrid(field.shape, cfg.domain_half_extent)
    spectrum = jnp.fft.fft2(field)
    intensity = field * field
    smooth = jnp.real(
        jnp.fft.ifft2(jnp.fft.fft2(intensity) * jnp.exp(-0.5 * cfg.sigma_smooth**2 * grid2))
    )
    mask = (jnp.sqrt(grid2 + 1e-12) <= cfg.kcut).astype(field.dtype)
    smooth = jnp.real(jnp.fft.ifft2(jnp.fft.fft2(smooth) * mask))
    smooth_fft = jnp.fft.fft2(smooth)
    grad_x = jnp.real(jnp.fft.ifft2(1j * grid_x * smooth_fft))
    grad_y = jnp.real(jnp.fft.ifft2(1j * grid_y * smooth_fft))
    force_x = (1.0 - cfg.chiral_mix) * grad_x + cfg.chiral_mix * (-grad_y)
    force_y = (1.0 - cfg.chiral_mix) * grad_y + cfg.chiral_mix * grad_x
    sigma = jnp.sqrt(jnp.mean(force_x * force_x + force_y * force_y) + 1e-12)
    force_x = (cfg.force_alpha0 / (sigma + 1e-12)) * force_x
    force_y = (cfg.force_alpha0 / (sigma + 1e-12)) * force_y
    magnitude = jnp.sqrt(force_x * force_x + force_y * force_y) + 1e-12
    saturation = 1.0 / (1.0 + magnitude / (cfg.force_max + 1e-12))
    force_x *= saturation
    force_y *= saturation
    divergence = jnp.real(
        jnp.fft.ifft2(
            1j * grid_x * jnp.fft.fft2(force_x)
            + 1j * grid_y * jnp.fft.fft2(force_y)
        )
    )
    laplacian = jnp.real(jnp.fft.ifft2(-grid2 * spectrum))
    rhs = cfg.diffusion * laplacian - cfg.decay * field + cfg.eta * divergence
    return field + cfg.field_dt * rhs


@jax.jit
def jax_step(
    state: JaxState,
    drive: jax.Array,
    weight: jax.Array,
    truth_flag: jax.Array,
    config: FireConfig,
) -> tuple[JaxState, FireMetrics]:
    key, noise_key = jax.random.split(state.key)
    next_field = _field_step(state.field, config)
    next_field = next_field + config.noise_scale * jax.random.normal(
        noise_key, next_field.shape, dtype=next_field.dtype
    )
    field_delta = next_field - state.field
    grad_y, grad_x = jnp.gradient(next_field)
    grad_rho = jnp.sqrt(jnp.mean(grad_x * grad_x + grad_y * grad_y))
    delta_tau_mass = jnp.mean(jnp.abs(field_delta))
    bloom_force = jnp.clip(
        config.bloom_grad_gain * grad_rho + config.bloom_dtau_gain * delta_tau_mass,
        -config.bloom_force_max,
        config.bloom_force_max,
    )

    delta = state.vector - state.previous
    identity = config.identity_alpha * state.previous + (1.0 - config.identity_alpha) * state.vector
    identity_drift = jnp.linalg.norm(identity - state.identity)
    coherence = state.vector.T @ weight @ state.vector
    fracture = jnp.linalg.norm(delta) / (jnp.linalg.norm(state.vector) + config.fracture_eta)
    realignment = (
        config.realign_alpha + config.realign_beta * config.fracture_grad_scale
    ) * delta
    candidate = state.vector + drive + bloom_force * state.coupling - realignment
    memory = (1.0 - config.memory_alpha) * state.memory + config.memory_alpha * candidate
    next_vector = (1.0 - config.dream_gamma) * candidate + config.dream_gamma * memory

    energy = jnp.mean(next_field * next_field) + 0.5 * jnp.sum(next_vector * next_vector)
    hdot = energy - state.energy_prev
    hdot_history = jnp.concatenate((state.hdot_history[1:], jnp.asarray([hdot], dtype=jnp.float32)))
    hdot_median = jnp.median(hdot_history)
    modes = jnp.fft.fft2(next_field) / next_field.size
    phase_norm = jnp.linalg.norm(jnp.abs(modes).reshape(-1)) / jnp.sqrt(
        jnp.maximum(1.0, modes.size)
    ) + 1e-9
    friend = 1.0 / (1.0 + fracture)

    fail_truth = jnp.logical_not(truth_flag)
    fail_phi = phase_norm < config.phi_min
    fail_wuwei = jnp.logical_and(config.require_wuwei, hdot_median >= 0.0)
    fail_friend = friend < config.friend_min
    fail_code = jnp.where(fail_truth, 1, 0)
    fail_code = jnp.where((fail_code == 0) & fail_phi, 2, fail_code)
    fail_code = jnp.where((fail_code == 0) & fail_wuwei, 3, fail_code)
    fail_code = jnp.where((fail_code == 0) & fail_friend, 4, fail_code)
    verdict = jnp.where(fail_code == 0, 1, 0).astype(jnp.int32)
    sentinel_allowed = (verdict == 1).astype(jnp.int32)

    next_state = JaxState(
        tick=state.tick + 1,
        vector=next_vector.astype(jnp.float32),
        previous=state.vector,
        identity=identity.astype(jnp.float32),
        field=next_field.astype(jnp.float32),
        memory=memory.astype(jnp.float32),
        hdot_history=hdot_history,
        energy_prev=energy.astype(jnp.float32),
        topology=state.topology,
        coupling=state.coupling,
        key=key,
    )
    return next_state, FireMetrics(
        coherence.astype(jnp.float32),
        fracture.astype(jnp.float32),
        identity_drift.astype(jnp.float32),
        phase_norm.astype(jnp.float32),
        hdot_median.astype(jnp.float32),
        friend.astype(jnp.float32),
        bloom_force.astype(jnp.float32),
        verdict,
        fail_code.astype(jnp.int32),
        sentinel_allowed,
    )


@jax.jit
def jax_rollout(state, drives, weight, truth_flags, config: FireConfig):
    def body(carry, inputs):
        drive, truth = inputs
        return jax_step(carry, drive, weight, truth, config)

    return jax.lax.scan(body, state, (drives, truth_flags))


def zero_extend_jax(state: JaxState, extra: int) -> JaxState:
    if extra < 0:
        raise ValueError("extra must be non-negative")
    return JaxState(
        tick=state.tick,
        vector=jnp.pad(state.vector, (0, extra)),
        previous=jnp.pad(state.previous, (0, extra)),
        identity=jnp.pad(state.identity, (0, extra)),
        field=state.field,
        memory=jnp.pad(state.memory, (0, extra)),
        hdot_history=state.hdot_history,
        energy_prev=state.energy_prev,
        topology=jnp.pad(state.topology, ((0, extra), (0, extra))),
        coupling=jnp.pad(state.coupling, (0, extra)),
        key=state.key,
    )
