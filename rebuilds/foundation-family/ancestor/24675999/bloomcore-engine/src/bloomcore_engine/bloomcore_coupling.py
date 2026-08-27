#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

# -*- coding: utf-8 -*-
"""
bloomcore_coupling.py

BLOOMCORE Coupling + Base PDE (JAX, pseudo-spectral)

This module is intentionally *pluggable*:
  • CouplingPolicy interface: apply(Xi, psi_hat, key) -> (Xi_next, psi_hat_next)
  • Built-in policies:
        - VelriaKaCompost
        - ΔΙΚΕ
        - LoveFilter
        - PolicyChain (compose multiple)
  • Base PDE step (spectral) and a canonical pipeline:
        PDE_step(u, ...) -> psi_hat -> CouplingPolicy.apply(Xi, psi_hat, key) -> u_next
  • step_jax + run_steps_jax
  • maybe_checkpoint_host() hook for cadence + hash discipline (host-side)

Notes:
  - This is a substrate-ready spine: the PDE is the physical carrier, policies are organs.
  - GPU/TPU-native. No CPU fallbacks inside jit/scan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Tuple, runtime_checkable

import jax
import jax.numpy as jnp
from jax import lax

# -------------------------
# CouplingPolicy interface
# -------------------------

@runtime_checkable
class CouplingPolicy(Protocol):
    """
    Pluggable strategy: one method.
    Implementers may mutate Xi and/or psi_hat.

    Contract:
      apply(Xi, psi_hat, key) -> (Xi_next, psi_hat_next)

    Shapes:
      Xi:      (H, W) real
      psi_hat: (H, W) real (you can treat it as intensity proxy or a "state readout")
      key:     PRNGKey
    """
    def apply(self, Xi: jnp.ndarray, psi_hat: jnp.ndarray, key: jax.Array) -> Tuple[jnp.ndarray, jnp.ndarray]: ...


@dataclass(frozen=True)
class PolicyChain(CouplingPolicy):
    """Compose multiple policies in order."""
    policies: Tuple[CouplingPolicy, ...]

    def apply(self, Xi: jnp.ndarray, psi_hat: jnp.ndarray, key: jax.Array) -> Tuple[jnp.ndarray, jnp.ndarray]:
        k = key
        for i, p in enumerate(self.policies):
            k, sub = jax.random.split(k)
            Xi, psi_hat = p.apply(Xi, psi_hat, sub)
        return Xi, psi_hat


# -------------------------
# Built-in policies (organs)
# -------------------------

@dataclass(frozen=True)
class VelriaKaCompost(CouplingPolicy):
    """
    Chiral micro-swirls in k-space to compost rigidity (break control ridges without destruction).
    """
    strength: float = 0.12
    band_lo: float = 0.28
    band_hi: float = 0.52

    def apply(self, Xi: jnp.ndarray, psi_hat: jnp.ndarray, key: jax.Array) -> Tuple[jnp.ndarray, jnp.ndarray]:
        H, W = Xi.shape
        kx = jnp.fft.fftfreq(W)
        ky = jnp.fft.fftfreq(H)
        KX, KY = jnp.meshgrid(kx, ky, indexing="xy")
        R = jnp.sqrt(KX * KX + KY * KY)

        F = jnp.fft.fft2(Xi)
        band = (R > self.band_lo) & (R < self.band_hi)

        # Chiral sign field: deterministic given grid; stochasticity can be introduced via strength jitter.
        jitter = 1.0 + 0.05 * jax.random.normal(key, ())
        s = jnp.clip(self.strength * jitter, 0.0, 0.95)

        swirl = jnp.exp(1j * (jnp.pi / 2.0) * jnp.sign(KX * KY + 1e-12))
        F2 = jnp.where(band, F * ((1.0 - s) * swirl), F)
        Xi2 = jnp.real(jnp.fft.ifft2(F2))

        return Xi2, psi_hat


@dataclass(frozen=True)
class ΔΙΚΕ(CouplingPolicy):
    """ΔΙΚΕ — justice without vengeance: re-center DC bias only when drift exceeds threshold."""
    threshold: float = 0.08
    recenter_gain: float = 0.7

    def apply(self, Xi: jnp.ndarray, psi_hat: jnp.ndarray, key: jax.Array) -> Tuple[jnp.ndarray, jnp.ndarray]:
        bias = jnp.mean(psi_hat)
        do = jnp.abs(bias) > self.threshold
        psi2 = jnp.where(do, jnp.clip(psi_hat - self.recenter_gain * bias, -1.0, 1.0), psi_hat)
        return Xi, psi2


# Back-compat alias (optional). Prefer ΔΙΚΕ.
DikeBalance = ΔΙΚΕ


@dataclass(frozen=True)
class LoveFilter(CouplingPolicy):
    """
    Love as a literal filter: k-space Gaussian coherence boost + thin horizon accent.
    """
    width: float = 0.12
    gain: float = 0.08
    horizon_width: float = 0.05

    def apply(self, Xi: jnp.ndarray, psi_hat: jnp.ndarray, key: jax.Array) -> Tuple[jnp.ndarray, jnp.ndarray]:
        H, W = psi_hat.shape
        kx = jnp.fft.fftfreq(W)
        ky = jnp.fft.fftfreq(H)
        KX, KY = jnp.meshgrid(kx, ky, indexing="xy")
        R2 = KX * KX + KY * KY

        G = jnp.exp(-R2 / (2.0 * (self.width ** 2) + 1e-12))
        horizon = 1.0 + self.gain * jnp.exp(-(KY * KY) / (2.0 * (self.horizon_width ** 2) + 1e-12))

        F = jnp.fft.fft2(psi_hat)
        psi2 = jnp.real(jnp.fft.ifft2(F * G * horizon))
        return Xi, psi2


# -------------------------
# Base PDE coupling (spectral)
# -------------------------

@dataclass(frozen=True)
class PDEConfig:
    """
    Base physical carrier (pseudo-spectral). Minimal but real.

    Evolution:
      u_{t+dt} = u + dt * [ D ∇²u - gamma u + eta * div( F(psi_hat) ) ]

    Where:
      psi_hat = observe(u, Xi, ...)  (default: psi_hat = u)
      F is derived from intensity I = |psi_hat|^2 and its gradients
    """
    dt: float = 0.05
    D: float = 0.15
    gamma: float = 0.15
    eta: float = 1.0

    # Force extraction
    force_mode: str = "mix"   # "lin" | "chiral" | "mix"
    chi: float = 0.6          # mixing weight for chiral component in "mix"
    alpha0: float = 1.2       # auto-gain numerator (scaled by grad magnitude)
    Fmax: float = 4.5         # saturation

    # Intensity smoothing + lowpass (k-space)
    sigma_smooth: float = 0.35
    kcut: float = 5.0

    # grid physical scale (only used to map k to radians)
    L: float = 8.0            # coordinate extent in each direction: [-L, L]


def _kgrid(H: int, W: int, L: float) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """
    Build k-space grids in radians per unit length.
    Using domain length = 2L, dx = 2L/W (approx for spectral operators).
    """
    dx = (2.0 * L) / W
    kx = 2.0 * jnp.pi * jnp.fft.fftfreq(W, d=dx)
    ky = 2.0 * jnp.pi * jnp.fft.fftfreq(H, d=dx)
    KX, KY = jnp.meshgrid(kx, ky, indexing="xy")
    K2 = KX * KX + KY * KY
    return KX, KY, K2


def _spectral_gaussian(Z: jnp.ndarray, K2: jnp.ndarray, sigma: float) -> jnp.ndarray:
    if sigma <= 0:
        return Z
    F = jnp.fft.fft2(Z)
    G = jnp.exp(-0.5 * (sigma ** 2) * K2)
    return jnp.real(jnp.fft.ifft2(F * G))


def _spectral_lowpass(Z: jnp.ndarray, K2: jnp.ndarray, kcut: float) -> jnp.ndarray:
    if (kcut is None) or (kcut <= 0):
        return Z
    F = jnp.fft.fft2(Z)
    K = jnp.sqrt(K2 + 1e-12)
    Lmask = (K <= kcut).astype(Z.dtype)
    return jnp.real(jnp.fft.ifft2(F * Lmask))


def _grad_spectral(Z: jnp.ndarray, KX: jnp.ndarray, KY: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
    F = jnp.fft.fft2(Z)
    gx = jnp.real(jnp.fft.ifft2(1j * KX * F))
    gy = jnp.real(jnp.fft.ifft2(1j * KY * F))
    return gx, gy


def _div_spectral(Fx: jnp.ndarray, Fy: jnp.ndarray, KX: jnp.ndarray, KY: jnp.ndarray) -> jnp.ndarray:
    FxF = jnp.fft.fft2(Fx)
    FyF = jnp.fft.fft2(Fy)
    div = jnp.real(jnp.fft.ifft2(1j * KX * FxF + 1j * KY * FyF))
    return div


def coupling_force_from_psi(
    psi_hat: jnp.ndarray,
    *,
    KX: jnp.ndarray,
    KY: jnp.ndarray,
    K2: jnp.ndarray,
    cfg: PDEConfig,
) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """
    Derive a force field F from intensity I = |psi_hat|^2.

    Returns:
      Fx, Fy, I_sm
    """
    I = psi_hat * psi_hat  # intensity proxy (real)

    # Smooth & lowpass in k-space for stability.
    I_sm = _spectral_gaussian(I, K2, cfg.sigma_smooth)
    I_sm = _spectral_lowpass(I_sm, K2, cfg.kcut)

    gx, gy = _grad_spectral(I_sm, KX, KY)

    if cfg.force_mode == "lin":
        Fx, Fy = gx, gy
    elif cfg.force_mode == "chiral":
        Fx, Fy = -gy, gx
    else:  # "mix"
        Fx = (1.0 - cfg.chi) * gx + cfg.chi * (-gy)
        Fy = (1.0 - cfg.chi) * gy + cfg.chi * (gx)

    # Auto-gain: normalize by grad magnitude scale (field-adaptive).
    sigma_g = jnp.sqrt(jnp.mean(Fx * Fx + Fy * Fy) + 1e-12)
    alpha = cfg.alpha0 / (sigma_g + 1e-12)
    Fx, Fy = alpha * Fx, alpha * Fy

    # Saturation to cap extremes.
    mag = jnp.sqrt(Fx * Fx + Fy * Fy) + 1e-12
    sat = 1.0 / (1.0 + (mag / (cfg.Fmax + 1e-12)))
    Fx, Fy = Fx * sat, Fy * sat

    return Fx, Fy, I_sm


def observe_psi_hat(u: jnp.ndarray, Xi: jnp.ndarray) -> jnp.ndarray:
    """
    Observation map: PDE carrier -> readout.
    Default: psi_hat is u (you can swap this later for a true Veil Ψ or multi-field readout).
    """
    return u


def PDE_step(u: jnp.ndarray, Xi: jnp.ndarray, cfg: PDEConfig) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """
    One pseudo-spectral PDE step.

    Returns:
      u_next, psi_hat, I_sm
    """
    H, W = u.shape
    KX, KY, K2 = _kgrid(H, W, cfg.L)

    psi_hat = observe_psi_hat(u, Xi)
    Fx, Fy, I_sm = coupling_force_from_psi(psi_hat, KX=KX, KY=KY, K2=K2, cfg=cfg)

    lap_u = jnp.real(jnp.fft.ifft2(-K2 * jnp.fft.fft2(u)))
    divF = _div_spectral(Fx, Fy, KX, KY)

    rhs = cfg.D * lap_u - cfg.gamma * u + cfg.eta * divF
    u_next = u + cfg.dt * rhs
    return u_next, psi_hat, I_sm


# -------------------------
# JAX step + scan runner
# -------------------------

@dataclass(frozen=True)
class BloomState:
    """
    Minimal BLOOMCORE step state for coupling loop.
    """
    tick: jnp.int32
    u: jnp.ndarray
    Xi: jnp.ndarray
    key: jax.Array


@dataclass(frozen=True)
class StepConfig:
    """
    Driver config for step_jax / run_steps_jax.
    """
    pde: PDEConfig
    # Xi update: EMA memory of processed psi_hat
    temporal_depth: int = 7
    Xi_mix: float = 0.5  # how strongly temporal_input (u) mixes into Xi-driven pre-inversion state (optional)


def _xi_ema_update(Xi: jnp.ndarray, psi_hat: jnp.ndarray, depth: int) -> jnp.ndarray:
    alpha = 2.0 / (depth + 1.0)
    return (1.0 - alpha) * Xi + alpha * psi_hat


def step_jax(
    st: BloomState,
    policy: CouplingPolicy,
    cfg: StepConfig,
) -> Tuple[BloomState, Dict[str, Any]]:
    """
    One full pipeline tick (device-native):

      PDE_step(u, Xi, ...) -> psi_hat
      policy.apply(Xi, psi_hat, key) -> (Xi', psi_hat')
      u_next computed using psi_hat from *current* u (already done in PDE_step), then Xi updated from psi_hat'

    We treat coupling as a "post-observation organ": it rewrites Xi and/or psi_hat
    that will shape the next tick's evolution.
    """
    key, sub = jax.random.split(st.key)

    # 1) Base physics step: produce u_next and a readout psi_hat from current u.
    u_next, psi_hat, _I = PDE_step(st.u, st.Xi, cfg.pde)

    # 2) Apply coupling policy (organs) to Xi and psi_hat.
    Xi2, psi2 = policy.apply(st.Xi, psi_hat, sub)

    # 3) Update Xi memory (Δ^τ EMA) from processed psi_hat.
    Xi_next = _xi_ema_update(Xi2, psi2, cfg.temporal_depth)

    st2 = BloomState(
        tick=st.tick + jnp.int32(1),
        u=u_next,
        Xi=Xi_next,
        key=key,
    )

    metrics = {
        "tick": st2.tick,
        "u_mean": jnp.mean(u_next),
        "u_std": jnp.std(u_next),
        "psi_mean": jnp.mean(psi2),
        "psi_std": jnp.std(psi2),
        "Xi_mean": jnp.mean(Xi_next),
        "Xi_std": jnp.std(Xi_next),
    }
    return st2, metrics


def run_steps_jax(
    st0: BloomState,
    policy: CouplingPolicy,
    cfg: StepConfig,
    *,
    steps: int,
) -> Tuple[BloomState, Dict[str, Any]]:
    """
    Scan runner (device-native). Returns final state and stacked metrics.
    """
    def body(st, _):
        st2, m = step_jax(st, policy, cfg)
        return st2, m

    stN, metrics = lax.scan(body, st0, xs=None, length=steps)
    return stN, metrics


# -------------------------
# Host-side checkpoint hook (lightweight)
# -------------------------

# This section is intentionally host-only and un-jitted.
# It gives you cadence + hash discipline without forcing determinism.

import hashlib
import time as _time
from dataclasses import field as _field


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass(frozen=True)
class CheckpointRef:
    tick: int
    xi_hash: str
    artifact_relpath: str
    artifact_sha256: str
    codec: str
    bytes_raw: int
    bytes_zstd: int


class CheckpointStore(Protocol):
    """
    Minimal host-side store interface. You can implement this with files, S3, blob, etc.
    """
    def save_xi(self, *, tick: int, Xi: jnp.ndarray) -> CheckpointRef: ...


# --- ADDED: Receipt hook interface (typed, minimal) ---
class ReceiptHook(Protocol):
    """
    Host-side receipt/telemetry hook.

    Implement:
      __call__(kind: str, payload: Dict[str, Any]) -> None
    """
    def __call__(self, kind: str, payload: Dict[str, Any]) -> None: ...


@dataclass
class CheckpointCtx:
    store: CheckpointStore
    emit_hook: Optional[ReceiptHook] = None  # callable(kind, payload)

    def emit(self, kind: str, payload: Dict[str, Any]) -> None:
        if self.emit_hook is not None:
            self.emit_hook(kind, payload)


def maybe_checkpoint_host(
    ctx: CheckpointCtx,
    st_device: BloomState,
    *,
    cadence: int = 64,
) -> Optional[CheckpointRef]:
    """
    Host boundary. Call this OUTSIDE jit/scan.

    Cadence:
      Every `cadence` ticks:
        • device_get(Xi)
        • ctx.store.save_xi(tick, Xi)
        • ctx.emit(BLOOMCORE.FIELD_CHECKPOINT.v1, ...)

    Hash discipline:
      - xi_hash is a content hash of raw float bytes (after device_get).
      - artifact_sha256 is what your store reports (e.g., compressed artifact hash).
    """
    tick = int(jax.device_get(st_device.tick))
    if cadence <= 0 or (tick % cadence) != 0:
        return None

    Xi_host = jax.device_get(st_device.Xi)

    # Stable host hashing: explicit float32 + C-order bytes
    import numpy as _np
    raw = _np.asarray(Xi_host, dtype=_np.float32).tobytes(order="C")
    xi_hash = _sha256_bytes(raw)

    ref = ctx.store.save_xi(tick=tick, Xi=Xi_host)

    ctx.emit("BLOOMCORE.FIELD_CHECKPOINT.v1", {
        "tick": tick,
        "Xi_hash": xi_hash,
        "artifact": {
            "relpath": ref.artifact_relpath,
            "sha256": ref.artifact_sha256,
            "codec": ref.codec,
            "bytes_raw": int(ref.bytes_raw),
            "bytes_zstd": int(ref.bytes_zstd),
        },
        "ts_utc": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime()),
    })
    return ref


# -------------------------
# Convenience builders
# -------------------------

def default_policy_chain_v12(
    *,
    velriaka_strength: float = 0.12,
    dike_threshold: float = 0.08,
    love_width: float = 0.12,
    love_gain: float = 0.08,
) -> CouplingPolicy:
    """
    Mirrors BLOOMCORE v1.2 organ order:
      compost → balance → love_filter
    """
    return PolicyChain((
        VelriaKaCompost(strength=velriaka_strength),
        ΔΙΚΕ(threshold=dike_threshold),
        LoveFilter(width=love_width, gain=love_gain),
    ))
