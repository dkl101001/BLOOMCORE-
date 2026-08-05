#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

# -*- coding: utf-8 -*-
"""theta_engine.py

Θ (theta) meta-dynamics for BLOOMCORE pseudo-spectral carriers.

This module is intentionally OSS-safe: it provides a general, auditable mechanism
to inject a wave-superposition-derived coherence force into an existing pseudo-spectral
PDE step, plus a minimal theta update rule.

Key idea
--------
Define a complex carrier wave superposition:

  Ψ(r,t) = Σ_n A_n * exp(i(α_n - k_n·r + ω_n t))

Then derive a potential V from its amplitude, and inject a force:

  F_Θ = λ * ∇V

where λ (lambda) is the scalar theta gain (or one component of θ).

Design constraints
------------------
* No changes required to the existing PDE_step() API.
* Uses spectral gradients (FFT-based) for clean GPU/TPU behavior.
* Keeps N (number of modes) small; vectorized real-space synthesis is used for simplicity.
* Provides receipts-ready metrics (norms, hashes) without imposing determinism.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Tuple

import jax
import jax.numpy as jnp
from jax import lax

from .bloomcore_coupling import CouplingPolicy, PDEConfig, StepConfig, _kgrid, _xi_ema_update


PotentialKind = Literal["abs", "abs2", "logabs2"]
ThetaUpdateKind = Literal["none", "gradnorm", "psi_std"]


@dataclass(frozen=True)
class ThetaWaveConfig:
    """Configuration for the Θ wave superposition force."""

    # Gain (θ scalar) bounds
    lam0: float = 0.6
    lam_min: float = 0.0
    lam_max: float = 8.0

    # Potential choice
    potential: PotentialKind = "abs2"  # "abs" | "abs2" | "logabs2"
    eps: float = 1e-6

    # Optional smoothing/lowpass on V to avoid spiky gradients (recommended)
    sigma_V: float = 0.25
    kcut_V: float = 8.0

    # Theta update rule
    update: ThetaUpdateKind = "gradnorm"
    lr: float = 0.15
    target_grad_norm: float = 1.0
    target_psi_std: float = 0.6


@dataclass(frozen=True)
class ThetaWaveState:
    """Dynamic state for Θ wave superposition."""

    tick: jnp.int32
    lam: jnp.ndarray  # scalar ()

    # Wave mode parameters (N,)
    A: jnp.ndarray
    alpha: jnp.ndarray
    kx: jnp.ndarray
    ky: jnp.ndarray
    omega: jnp.ndarray


def theta_init(
    *,
    key: jax.Array,
    N: int,
    cfg: ThetaWaveConfig,
    k_scale: float = 2.0,
) -> ThetaWaveState:
    """Initialize a ThetaWaveState with N random modes.

    k_scale sets the typical magnitude of k (radians per unit length), prior to mapping to grid.
    """
    k1, k2, k3, k4, k5 = jax.random.split(key, 5)
    A = 0.6 + 0.4 * jax.random.uniform(k1, (N,))
    alpha = 2.0 * jnp.pi * jax.random.uniform(k2, (N,))

    # Random directions, moderately band-limited magnitudes
    ang = 2.0 * jnp.pi * jax.random.uniform(k3, (N,))
    kmag = k_scale * (0.25 + 0.75 * jax.random.uniform(k4, (N,)))
    kx = kmag * jnp.cos(ang)
    ky = kmag * jnp.sin(ang)

    omega = 0.5 + 1.5 * jax.random.uniform(k5, (N,))

    return ThetaWaveState(
        tick=jnp.int32(0),
        lam=jnp.asarray(cfg.lam0, dtype=jnp.float32),
        A=jnp.asarray(A, dtype=jnp.float32),
        alpha=jnp.asarray(alpha, dtype=jnp.float32),
        kx=jnp.asarray(kx, dtype=jnp.float32),
        ky=jnp.asarray(ky, dtype=jnp.float32),
        omega=jnp.asarray(omega, dtype=jnp.float32),
    )


def _spectral_gaussian_real(Z: jnp.ndarray, K2: jnp.ndarray, sigma: float) -> jnp.ndarray:
    if sigma <= 0:
        return Z
    F = jnp.fft.fft2(Z)
    G = jnp.exp(-0.5 * (sigma ** 2) * K2)
    return jnp.real(jnp.fft.ifft2(F * G))


def _spectral_lowpass_real(Z: jnp.ndarray, K2: jnp.ndarray, kcut: float) -> jnp.ndarray:
    if (kcut is None) or (kcut <= 0):
        return Z
    F = jnp.fft.fft2(Z)
    K = jnp.sqrt(K2 + 1e-12)
    mask = (K <= kcut).astype(Z.dtype)
    return jnp.real(jnp.fft.ifft2(F * mask))


def _grad_spectral_real(Z: jnp.ndarray, KX: jnp.ndarray, KY: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
    F = jnp.fft.fft2(Z)
    gx = jnp.real(jnp.fft.ifft2(1j * KX * F))
    gy = jnp.real(jnp.fft.ifft2(1j * KY * F))
    return gx, gy


def synthesize_Psi(
    *,
    H: int,
    W: int,
    L: float,
    tick: jnp.ndarray,
    st: ThetaWaveState,
) -> jnp.ndarray:
    """Synthesize Ψ(r,t) in real space (complex64), vectorized across modes."""
    # Coordinate grid r = (x,y)
    x = jnp.linspace(-L, L, W, dtype=jnp.float32)
    y = jnp.linspace(-L, L, H, dtype=jnp.float32)
    X, Y = jnp.meshgrid(x, y, indexing="xy")

    # Mode phases: (N,H,W)
    # phase = α - (kx*X + ky*Y) + ω*t
    t = st.tick.astype(jnp.float32)  # discrete time index; actual dt scaling can be folded into omega
    phase = (
        st.alpha[:, None, None]
        - (st.kx[:, None, None] * X[None, :, :] + st.ky[:, None, None] * Y[None, :, :])
        + st.omega[:, None, None] * t
    )
    # Complex wave per mode
    Psi_n = st.A[:, None, None] * (jnp.cos(phase) + 1j * jnp.sin(phase))
    Psi = jnp.sum(Psi_n, axis=0)
    return Psi.astype(jnp.complex64)


def potential_from_Psi(Psi: jnp.ndarray, *, kind: PotentialKind, eps: float) -> jnp.ndarray:
    amp2 = jnp.real(Psi * jnp.conj(Psi))  # |Psi|^2
    if kind == "abs":
        return jnp.sqrt(amp2 + eps)
    if kind == "logabs2":
        return jnp.log(amp2 + eps)
    return amp2


def theta_force(
    *,
    cfg_pde: PDEConfig,
    cfg_theta: ThetaWaveConfig,
    st_theta: ThetaWaveState,
) -> Tuple[jnp.ndarray, jnp.ndarray, Dict[str, Any]]:
    """Deprecated placeholder.

    Keep this symbol out of the public surface until/unless we want a dedicated
    force-only API. For now, use PDE_step_with_theta().
    """
    raise NotImplementedError("Use PDE_step_with_theta().")


def PDE_step_with_theta(
    u: jnp.ndarray,
    Xi: jnp.ndarray,
    cfg_pde: PDEConfig,
    st_theta: ThetaWaveState,
    cfg_theta: ThetaWaveConfig,
) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, ThetaWaveState, Dict[str, Any]]:
    """One pseudo-spectral PDE step with an additive Θ-wave coherence force.

    Returns:
      u_next, psi_hat, I_sm, theta_state_next, theta_metrics
    """
    H, W = u.shape
    KX, KY, K2 = _kgrid(H, W, cfg_pde.L)

    # Base readout follows bloomcore_coupling.observe_psi_hat default (psi_hat = u)
    psi_hat = u

    # Base force from psi_hat intensity (matches bloomcore_coupling.coupling_force_from_psi)
    I = psi_hat * psi_hat
    I_sm = _spectral_gaussian_real(I, K2, cfg_pde.sigma_smooth)
    I_sm = _spectral_lowpass_real(I_sm, K2, cfg_pde.kcut)
    gx, gy = _grad_spectral_real(I_sm, KX, KY)
    if cfg_pde.force_mode == "lin":
        Fx0, Fy0 = gx, gy
    elif cfg_pde.force_mode == "chiral":
        Fx0, Fy0 = -gy, gx
    else:
        Fx0 = (1.0 - cfg_pde.chi) * gx + cfg_pde.chi * (-gy)
        Fy0 = (1.0 - cfg_pde.chi) * gy + cfg_pde.chi * (gx)
    sigma_g = jnp.sqrt(jnp.mean(Fx0 * Fx0 + Fy0 * Fy0) + 1e-12)
    alpha = cfg_pde.alpha0 / (sigma_g + 1e-12)
    Fx0, Fy0 = alpha * Fx0, alpha * Fy0
    mag0 = jnp.sqrt(Fx0 * Fx0 + Fy0 * Fy0) + 1e-12
    sat0 = 1.0 / (1.0 + (mag0 / (cfg_pde.Fmax + 1e-12)))
    Fx0, Fy0 = Fx0 * sat0, Fy0 * sat0

    # Θ-wave force: Ψ synthesis -> V -> ∇V -> λ∇V
    Psi = synthesize_Psi(H=H, W=W, L=cfg_pde.L, tick=st_theta.tick, st=st_theta)
    V = potential_from_Psi(Psi, kind=cfg_theta.potential, eps=cfg_theta.eps)
    V = _spectral_gaussian_real(V, K2, cfg_theta.sigma_V)
    V = _spectral_lowpass_real(V, K2, cfg_theta.kcut_V)
    gVx, gVy = _grad_spectral_real(V, KX, KY)

    Fx1 = st_theta.lam * gVx
    Fy1 = st_theta.lam * gVy

    # Total force
    Fx = Fx0 + Fx1
    Fy = Fy0 + Fy1

    # PDE update
    lap_u = jnp.real(jnp.fft.ifft2(-K2 * jnp.fft.fft2(u)))
    divF = jnp.real(jnp.fft.ifft2(1j * KX * jnp.fft.fft2(Fx) + 1j * KY * jnp.fft.fft2(Fy)))
    rhs = cfg_pde.D * lap_u - cfg_pde.gamma * u + cfg_pde.eta * divF
    u_next = u + cfg_pde.dt * rhs

    # θ update (minimal, auditable)
    gradnorm = jnp.sqrt(jnp.mean(gVx * gVx + gVy * gVy) + 1e-12)
    psi_std = jnp.std(psi_hat)

    lam = st_theta.lam
    if cfg_theta.update == "gradnorm":
        # Push λ up if ∥∇V∥ is small; down if too large
        err = cfg_theta.target_grad_norm - gradnorm
        lam = lam + cfg_theta.lr * err
    elif cfg_theta.update == "psi_std":
        err = cfg_theta.target_psi_std - psi_std
        lam = lam + cfg_theta.lr * err

    lam = jnp.clip(lam, cfg_theta.lam_min, cfg_theta.lam_max)
    st_theta2 = ThetaWaveState(
        tick=st_theta.tick + jnp.int32(1),
        lam=lam,
        A=st_theta.A,
        alpha=st_theta.alpha,
        kx=st_theta.kx,
        ky=st_theta.ky,
        omega=st_theta.omega,
    )

    metrics: Dict[str, Any] = {
        "theta_tick": st_theta2.tick,
        "theta_lam": lam,
        "theta_gradnorm": gradnorm,
        "theta_psi_std": psi_std,
        "V_mean": jnp.mean(V),
        "V_std": jnp.std(V),
        "Fx1_rms": jnp.sqrt(jnp.mean(Fx1 * Fx1) + 1e-12),
        "Fy1_rms": jnp.sqrt(jnp.mean(Fy1 * Fy1) + 1e-12),
    }

    return u_next, psi_hat, I_sm, st_theta2, metrics


# -------------------------
# JAX step + scan runner (Θ-augmented)
# -------------------------


@dataclass(frozen=True)
class BloomThetaState:
    """Device-native state for the Θ-augmented coupling loop.

    This mirrors bloomcore_coupling.BloomState but carries an additional
    ThetaWaveState for the additive Ψ-drive force.
    """

    tick: jnp.int32
    u: jnp.ndarray
    Xi: jnp.ndarray
    theta: ThetaWaveState
    key: jax.Array


def step_jax_with_theta(
    st: BloomThetaState,
    policy: CouplingPolicy,
    cfg: StepConfig,
    cfg_theta: ThetaWaveConfig,
) -> Tuple[BloomThetaState, Dict[str, Any]]:
    """One full pipeline tick with Θ-wave force (device-native).

    Order (matches the base engine's semantics):
      1) PDE_step_with_theta produces u_next and psi_hat from current u.
      2) policy.apply mutates Xi and/or psi_hat.
      3) Xi EMA updated from processed psi_hat.
      4) Θ state already advanced within PDE_step_with_theta.
    """

    key, sub = jax.random.split(st.key)

    # 1) Physics + Θ force
    u_next, psi_hat, _I_sm, theta2, theta_metrics = PDE_step_with_theta(
        st.u, st.Xi, cfg.pde, st.theta, cfg_theta
    )

    # 2) Organs (coupling policy)
    Xi2, psi2 = policy.apply(st.Xi, psi_hat, sub)

    # 3) Xi memory (Δ^τ EMA)
    Xi_next = _xi_ema_update(Xi2, psi2, cfg.temporal_depth)

    st2 = BloomThetaState(
        tick=st.tick + jnp.int32(1),
        u=u_next,
        Xi=Xi_next,
        theta=theta2,
        key=key,
    )

    metrics: Dict[str, Any] = {
        "tick": st2.tick,
        "u_mean": jnp.mean(u_next),
        "u_std": jnp.std(u_next),
        "psi_mean": jnp.mean(psi2),
        "psi_std": jnp.std(psi2),
        "Xi_mean": jnp.mean(Xi_next),
        "Xi_std": jnp.std(Xi_next),
    }
    metrics.update(theta_metrics)
    return st2, metrics


def run_steps_jax_with_theta(
    st0: BloomThetaState,
    policy: CouplingPolicy,
    cfg: StepConfig,
    cfg_theta: ThetaWaveConfig,
    *,
    steps: int,
) -> Tuple[BloomThetaState, Dict[str, Any]]:
    """Scan runner (device-native) for Θ-augmented coupling.

    Returns final state and stacked metrics dict.
    """

    def body(st, _):
        st2, m = step_jax_with_theta(st, policy, cfg, cfg_theta)
        return st2, m

    stN, metrics = lax.scan(body, st0, xs=None, length=steps)
    return stN, metrics
