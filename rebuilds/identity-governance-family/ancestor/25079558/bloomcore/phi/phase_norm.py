# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from typing import Tuple
import numpy as np

# Optional JAX
try:
    import jax.numpy as jnp  # type: ignore
except Exception:  # pragma: no cover
    jnp = None  # type: ignore

def branchial_weights_np(Bn: np.ndarray, alpha_branch: float) -> np.ndarray:
    Bn = np.asarray(Bn, dtype=float)
    w = np.exp(alpha_branch * (Bn - np.max(Bn)))
    w = w / np.sum(w)
    return w

def phase_norm_branchial_np(Phi_modes: np.ndarray, Bn: np.ndarray, alpha_branch: float, eps: float) -> float:
    Phi_modes = np.asarray(Phi_modes, dtype=float)
    w = branchial_weights_np(Bn, alpha_branch)
    z = np.sum(w * np.exp(1j * Phi_modes))
    return float(np.abs(z) + eps)

def branchial_weights(Bn, alpha_branch: float):
    """JAX-first if available; NumPy otherwise."""
    if jnp is None:
        return branchial_weights_np(np.asarray(Bn), alpha_branch)
    Bn = jnp.asarray(Bn)
    w = jnp.exp(alpha_branch * (Bn - jnp.max(Bn)))
    w = w / jnp.sum(w)
    return w

def phase_norm_branchial(Phi_modes, Bn, alpha_branch: float, eps: float):
    """N_phase = |Σ w_n(B) e^{i Φ_n}| + eps (JAX-first)."""
    if jnp is None:
        return phase_norm_branchial_np(np.asarray(Phi_modes), np.asarray(Bn), alpha_branch, eps)
    Phi_modes = jnp.asarray(Phi_modes)
    w = branchial_weights(Bn, alpha_branch)
    z = jnp.sum(w * jnp.exp(1j * Phi_modes))
    return jnp.abs(z) + eps
