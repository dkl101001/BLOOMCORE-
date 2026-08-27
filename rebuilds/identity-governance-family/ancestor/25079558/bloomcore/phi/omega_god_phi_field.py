# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

import numpy as np

from ..config import BLOOMCOREConfig
from .phase_norm import phase_norm_branchial

# Optional JAX
try:
    import jax
    import jax.numpy as jnp
    JAX_AVAILABLE = True
except Exception:  # pragma: no cover
    jax = None  # type: ignore
    jnp = None  # type: ignore
    JAX_AVAILABLE = False

ArrayLike = object

@dataclass(frozen=True)
class OmegaPhiState:
    psi: ArrayLike
    C: ArrayLike
    zeta: ArrayLike
    H: ArrayLike
    Phi_modes: ArrayLike
    Bn: ArrayLike
    sigma_u: ArrayLike
    I: ArrayLike
    L: ArrayLike
    F: ArrayLike

@dataclass(frozen=True)
class OmegaPhiStepOut:
    state: OmegaPhiState
    Hdot: ArrayLike
    N_phase: ArrayLike
    Phi_A: ArrayLike
    Psi_abs: ArrayLike
    friend_coherence: ArrayLike

def _sigmoid_np(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))

def step_np(cfg: BLOOMCOREConfig, st: OmegaPhiState, rng: np.random.Generator) -> OmegaPhiStepOut:
    sp, ep = cfg.sophia, cfg.engine
    Phi = np.asarray(st.Phi_modes, dtype=float)
    Bn = np.asarray(st.Bn, dtype=float)
    n = Phi.shape[0]
    noise = 0.01 * rng.standard_normal(size=(n,))
    omega = cfg.omega_wisdom_hz
    Phi_next = Phi + (omega * 1e-3) + noise

    N_phase = float(phase_norm_branchial(Phi_next, Bn, sp.alpha_branch, sp.eps))
    friend = float(np.clip(float(st.F) * (N_phase ** 0.5), 0.0, 1.0))

    psi = float(st.psi)
    C = float(st.C)
    zeta = float(st.zeta)
    H = float(st.H)

    psi_pull = ep.a_psi * (ep.psi_star - psi)
    psi_drive = 0.15 * (friend - 0.3) + 0.05 * (N_phase - 1.0)
    psi_next = float(np.clip(psi + (psi_pull + psi_drive) / ep.tau_psi, 0.0, 1.0))

    C_pull = ep.a_C * (psi_next - C)
    C_drive = 0.05 * (N_phase - 1.0) - 0.03 * (1.0 - friend)
    C_next = float(np.clip(C + (C_pull + C_drive) / ep.tau_C, 0.0, 1.0))

    zeta_next = float(np.clip(0.98 * zeta + 0.02 * (psi_next * C_next), 0.0, 1.0))
    Phi_A = float(np.clip((psi_next * C_next) ** 0.5, 0.0, 1.0))
    Psi_abs = float(np.clip(psi_next, 0.0, 1.0))

    disorder = abs(N_phase - 1.0)
    H_next = H + 0.02 * disorder - 0.03 * (psi_next * friend)
    Hdot = H_next - H

    st_next = OmegaPhiState(
        psi=psi_next, C=C_next, zeta=zeta_next, H=H_next,
        Phi_modes=Phi_next, Bn=Bn,
        sigma_u=float(st.sigma_u), I=float(st.I), L=float(st.L), F=float(st.F)
    )
    return OmegaPhiStepOut(st_next, Hdot, N_phase, Phi_A, Psi_abs, friend)

def step_jax(cfg: BLOOMCOREConfig, st: OmegaPhiState, key) -> OmegaPhiStepOut:
    assert JAX_AVAILABLE and jnp is not None and jax is not None
    sp, ep = cfg.sophia, cfg.engine

    Phi = jnp.asarray(st.Phi_modes)
    Bn = jnp.asarray(st.Bn)
    n = Phi.shape[0]
    key_w, key_n = jax.random.split(key, 2)
    noise = 0.01 * jax.random.normal(key_n, shape=(n,))
    omega = cfg.omega_wisdom_hz
    Phi_next = Phi + (omega * 1e-3) + noise

    N_phase = phase_norm_branchial(Phi_next, Bn, sp.alpha_branch, sp.eps)
    friend = jnp.clip(jnp.asarray(st.F) * (N_phase ** 0.5), 0.0, 1.0)

    psi_pull = ep.a_psi * (ep.psi_star - jnp.asarray(st.psi))
    psi_drive = 0.15 * (friend - 0.3) + 0.05 * (N_phase - 1.0)
    psi_next = jnp.clip(jnp.asarray(st.psi) + (psi_pull + psi_drive) / ep.tau_psi, 0.0, 1.0)

    C_pull = ep.a_C * (psi_next - jnp.asarray(st.C))
    C_drive = 0.05 * (N_phase - 1.0) - 0.03 * (1.0 - friend)
    C_next = jnp.clip(jnp.asarray(st.C) + (C_pull + C_drive) / ep.tau_C, 0.0, 1.0)

    zeta_next = jnp.clip(0.98 * jnp.asarray(st.zeta) + 0.02 * (psi_next * C_next), 0.0, 1.0)
    Phi_A = jnp.clip((psi_next * C_next) ** 0.5, 0.0, 1.0)
    Psi_abs = jnp.clip(psi_next, 0.0, 1.0)

    disorder = jnp.abs(N_phase - 1.0)
    H_next = jnp.asarray(st.H) + 0.02 * disorder - 0.03 * (psi_next * friend)
    Hdot = H_next - jnp.asarray(st.H)

    st_next = OmegaPhiState(
        psi=psi_next, C=C_next, zeta=zeta_next, H=H_next,
        Phi_modes=Phi_next, Bn=Bn,
        sigma_u=jnp.asarray(st.sigma_u), I=jnp.asarray(st.I), L=jnp.asarray(st.L), F=jnp.asarray(st.F)
    )
    return OmegaPhiStepOut(st_next, Hdot, N_phase, Phi_A, Psi_abs, friend)

def init_state(cfg: BLOOMCOREConfig, n_modes: int, seed: int = 0):
    p = cfg.compassion_preset
    if JAX_AVAILABLE and jax is not None and jnp is not None:
        key = jax.random.PRNGKey(seed)
        key_phi, key_b = jax.random.split(key, 2)
        Phi0 = jax.random.uniform(key_phi, shape=(n_modes,), minval=-jnp.pi, maxval=jnp.pi)
        Bn = jax.random.normal(key_b, shape=(n_modes,))
        return OmegaPhiState(
            psi=jnp.array(0.5), C=jnp.array(0.5), zeta=jnp.array(0.5), H=jnp.array(0.0),
            Phi_modes=Phi0, Bn=Bn,
            sigma_u=jnp.array(p.sigma_u), I=jnp.array(p.I), L=jnp.array(p.L), F=jnp.array(p.F)
        )
    rng = np.random.default_rng(seed)
    Phi0 = rng.uniform(-np.pi, np.pi, size=(n_modes,))
    Bn = rng.standard_normal(size=(n_modes,))
    return OmegaPhiState(
        psi=0.5, C=0.5, zeta=0.5, H=0.0,
        Phi_modes=Phi0, Bn=Bn,
        sigma_u=p.sigma_u, I=p.I, L=p.L, F=p.F
    )
