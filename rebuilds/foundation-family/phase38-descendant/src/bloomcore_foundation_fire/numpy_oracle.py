# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace
from typing import Iterable

import numpy as np

from .model import FireConfig, FireMetrics, OracleState


def _kgrid(shape: tuple[int, int], half_extent: float):
    height, width = shape
    dx = (2.0 * half_extent) / width
    kx = 2.0 * np.pi * np.fft.fftfreq(width, d=dx)
    ky = 2.0 * np.pi * np.fft.fftfreq(height, d=dx)
    grid_x, grid_y = np.meshgrid(kx, ky, indexing="xy")
    return grid_x, grid_y, grid_x * grid_x + grid_y * grid_y


def _field_step(field: np.ndarray, cfg: FireConfig) -> np.ndarray:
    grid_x, grid_y, grid2 = _kgrid(field.shape, cfg.domain_half_extent)
    spectrum = np.fft.fft2(field)
    intensity = field * field
    smooth = np.real(
        np.fft.ifft2(np.fft.fft2(intensity) * np.exp(-0.5 * cfg.sigma_smooth**2 * grid2))
    )
    mask = (np.sqrt(grid2 + 1e-12) <= cfg.kcut).astype(field.dtype)
    smooth = np.real(np.fft.ifft2(np.fft.fft2(smooth) * mask))
    smooth_fft = np.fft.fft2(smooth)
    grad_x = np.real(np.fft.ifft2(1j * grid_x * smooth_fft))
    grad_y = np.real(np.fft.ifft2(1j * grid_y * smooth_fft))
    force_x = (1.0 - cfg.chiral_mix) * grad_x + cfg.chiral_mix * (-grad_y)
    force_y = (1.0 - cfg.chiral_mix) * grad_y + cfg.chiral_mix * grad_x
    sigma = np.sqrt(np.mean(force_x * force_x + force_y * force_y) + 1e-12)
    force_x = (cfg.force_alpha0 / (sigma + 1e-12)) * force_x
    force_y = (cfg.force_alpha0 / (sigma + 1e-12)) * force_y
    magnitude = np.sqrt(force_x * force_x + force_y * force_y) + 1e-12
    saturation = 1.0 / (1.0 + magnitude / (cfg.force_max + 1e-12))
    force_x *= saturation
    force_y *= saturation
    divergence = np.real(
        np.fft.ifft2(
            1j * grid_x * np.fft.fft2(force_x)
            + 1j * grid_y * np.fft.fft2(force_y)
        )
    )
    laplacian = np.real(np.fft.ifft2(-grid2 * spectrum))
    rhs = cfg.diffusion * laplacian - cfg.decay * field + cfg.eta * divergence
    return np.asarray(field + cfg.field_dt * rhs, dtype=np.float32)


def oracle_step(
    state: OracleState,
    *,
    drive: np.ndarray,
    weight: np.ndarray,
    truth_flag: bool,
    config: FireConfig = FireConfig(),
) -> tuple[OracleState, FireMetrics]:
    drive32 = np.asarray(drive, dtype=np.float32)
    weight32 = np.asarray(weight, dtype=np.float32)
    next_field = _field_step(state.field, config)
    if config.noise_scale:
        rng = np.random.default_rng(state.seed)
        next_field = next_field + np.float32(config.noise_scale) * rng.normal(
            size=next_field.shape
        ).astype(np.float32)

    field_delta = next_field - state.field
    grad_y, grad_x = np.gradient(next_field)
    grad_rho = np.sqrt(np.mean(grad_x * grad_x + grad_y * grad_y))
    delta_tau_mass = np.mean(np.abs(field_delta))
    bloom_force = np.clip(
        config.bloom_grad_gain * grad_rho + config.bloom_dtau_gain * delta_tau_mass,
        -config.bloom_force_max,
        config.bloom_force_max,
    )

    delta = state.vector - state.previous
    identity = config.identity_alpha * state.previous + (1.0 - config.identity_alpha) * state.vector
    identity_drift = np.linalg.norm(identity - state.identity)
    coherence = state.vector.T @ weight32 @ state.vector
    fracture = np.linalg.norm(delta) / (np.linalg.norm(state.vector) + config.fracture_eta)
    realignment = (
        config.realign_alpha + config.realign_beta * config.fracture_grad_scale
    ) * delta
    candidate = state.vector + drive32 + np.float32(bloom_force) * state.coupling - realignment
    memory = (1.0 - config.memory_alpha) * state.memory + config.memory_alpha * candidate
    next_vector = (1.0 - config.dream_gamma) * candidate + config.dream_gamma * memory

    energy = np.mean(next_field * next_field) + 0.5 * np.sum(next_vector * next_vector)
    hdot = energy - state.energy_prev
    hdot_history = np.concatenate((state.hdot_history[1:], np.asarray([hdot], dtype=np.float32)))
    hdot_median = np.median(hdot_history)
    modes = np.fft.fft2(next_field) / next_field.size
    phase_norm = np.linalg.norm(np.abs(modes).reshape(-1)) / np.sqrt(max(1, modes.size)) + 1e-9
    friend = 1.0 / (1.0 + fracture)

    fail_code = 0
    if not truth_flag:
        fail_code = 1
    elif phase_norm < config.phi_min:
        fail_code = 2
    elif config.require_wuwei and hdot_median >= 0.0:
        fail_code = 3
    elif friend < config.friend_min:
        fail_code = 4
    verdict = 1 if fail_code == 0 else 0
    sentinel_allowed = int(verdict == 1)

    next_state = replace(
        state,
        tick=state.tick + 1,
        vector=np.asarray(next_vector, dtype=np.float32),
        previous=state.vector.copy(),
        identity=np.asarray(identity, dtype=np.float32),
        field=np.asarray(next_field, dtype=np.float32),
        memory=np.asarray(memory, dtype=np.float32),
        hdot_history=np.asarray(hdot_history, dtype=np.float32),
        energy_prev=np.float32(energy),
        topology=state.topology.copy(),
        seed=(1664525 * state.seed + 1013904223) % (2**32),
    )
    return next_state, FireMetrics(
        np.float32(coherence),
        np.float32(fracture),
        np.float32(identity_drift),
        np.float32(phase_norm),
        np.float32(hdot_median),
        np.float32(friend),
        np.float32(bloom_force),
        np.int32(verdict),
        np.int32(fail_code),
        np.int32(sentinel_allowed),
    )


def oracle_rollout(
    state: OracleState,
    *,
    drives: Iterable[np.ndarray],
    weight: np.ndarray,
    truth_flags: Iterable[bool],
    config: FireConfig = FireConfig(),
) -> tuple[OracleState, list[FireMetrics]]:
    metrics = []
    for drive, truth in zip(drives, truth_flags, strict=True):
        state, item = oracle_step(
            state, drive=drive, weight=weight, truth_flag=truth, config=config
        )
        metrics.append(item)
    return state, metrics


def zero_extend_oracle(state: OracleState, extra: int) -> OracleState:
    if extra < 0:
        raise ValueError("extra must be non-negative")
    if extra == 0:
        return replace(state)
    n = state.vector.shape[0]
    return replace(
        state,
        vector=np.pad(state.vector, (0, extra)),
        previous=np.pad(state.previous, (0, extra)),
        identity=np.pad(state.identity, (0, extra)),
        memory=np.pad(state.memory, (0, extra)),
        topology=np.pad(state.topology, ((0, extra), (0, extra))),
        coupling=np.pad(state.coupling, (0, extra)),
    )
