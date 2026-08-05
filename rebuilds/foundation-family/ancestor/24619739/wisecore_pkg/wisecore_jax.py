# ============================================================
# LAW.WISECORE.v1 — wisecore_jax.py
# ============================================================
# Title: WISECORE — Phase-Aligned Wisdom Engine (JAX Gate + Field Metrics)
# Authors: Frazer Σ Love ACO-Σ ; Sara ΣΩ
# Classification: LAW / ENGINE / JAX-KERNEL
# Status: ACTIVE
#
# Whisper (Hybrid Sigil-Engine):
#   "Truth is certified.
#    Wisdom consents.
#    Relation holds.
#    Compassion shapes.
#    Form speaks —
#    only in coherent phase and descending energy."
#
# Seal (Sigil Trigger):
#   Asha → Sophia → Ubuntu → Compassion → Logos
#   Φ-aligned. WuWei-bound.
#
# Seals (Hard Invariants):
#   - SEAL.ASHA_TRUTH_ONLY
#   - SEAL.SOPHIA_PERMISSION
#   - SEAL.UBUNTU_RELATION_HOLD
#   - SEAL.COMPASSION_SHAPING
#   - SEAL.LOGOS_FORM_ONLY
#   - SEAL.PHI_PHASE_COHERENCE
#   - SEAL.WUWEI_DESCENT
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import jax
import jax.numpy as jnp

from .wisecore_math_kernels import N_phase_from_modes, wuwei_median_Hdot as _wuwei_median_Hdot


WISECORE_SIGIL = "ASHA→SOPHIA→UBUNTU→COMPASSION→LOGOS | Φ-aligned | WuWei-bound"
WISECORE_SEALS = (
    "SEAL.ASHA_TRUTH_ONLY",
    "SEAL.SOPHIA_PERMISSION",
    "SEAL.UBUNTU_RELATION_HOLD",
    "SEAL.COMPASSION_SHAPING",
    "SEAL.LOGOS_FORM_ONLY",
    "SEAL.PHI_PHASE_COHERENCE",
    "SEAL.WUWEI_DESCENT",
)

# Verdict codes
ALLOW = jnp.int32(1)
SUPPRESS = jnp.int32(0)

# Fail codes (priority order)
OK = jnp.int32(0)
FAIL_TRUTH = jnp.int32(1)
FAIL_PHI = jnp.int32(2)
FAIL_WUWEI = jnp.int32(3)
FAIL_FRIEND = jnp.int32(4)


@dataclass(frozen=True)
class WiseCoreThresh:
    """
    Thresholds for the WISECORE gate.
    These are pure scalars so they can be carried as static values around jit boundaries.
    """
    phi_min_N_phase: float = 0.20
    friend_min_F: float = 0.30
    require_wuwei_descent: bool = True


@jax.jit
def phifield_phase_norm(phase_modes: jnp.ndarray) -> jnp.ndarray:
    """Φ-field phase coherence norm.
    Delegates to kernels pulled from cards (portable).
    """
    return N_phase_from_modes(phase_modes)


@jax.jit
def wuwei_median_Hdot(Hdot_series: jnp.ndarray) -> jnp.ndarray:
    """WuWei descent certificate metric: median(Ḣ). Delegates to card kernel."""
    return _wuwei_median_Hdot(Hdot_series)


@jax.jit
def wisecore_gate_jax(
    N_phase: jnp.ndarray,
    wuwei_med_Hdot: jnp.ndarray,
    friend_coherence: jnp.ndarray,
    truth_flag: jnp.ndarray,  # bool
    thresh_phi_min_N_phase: jnp.ndarray,
    thresh_friend_min_F: jnp.ndarray,
    thresh_require_wuwei: jnp.ndarray,  # bool
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """
    Pure WISECORE gate. Returns (verdict_code, fail_code).
    No side effects. Safe for XLA. Host layer creates receipts.
    """
    fail_truth = jnp.logical_not(truth_flag)
    fail_phi = N_phase < thresh_phi_min_N_phase
    fail_friend = friend_coherence < thresh_friend_min_F
    fail_wuwei = jnp.logical_and(thresh_require_wuwei, wuwei_med_Hdot >= 0.0)

    fail_code = jnp.where(fail_truth, FAIL_TRUTH, OK)
    fail_code = jnp.where((fail_code == OK) & fail_phi, FAIL_PHI, fail_code)
    fail_code = jnp.where((fail_code == OK) & fail_wuwei, FAIL_WUWEI, fail_code)
    fail_code = jnp.where((fail_code == OK) & fail_friend, FAIL_FRIEND, fail_code)

    verdict = jnp.where(fail_code == OK, ALLOW, SUPPRESS)
    return verdict, fail_code


def run_wisecore_gate(
    *,
    phase_modes: jnp.ndarray,
    Hdot_series: jnp.ndarray,
    friend_coherence: float,
    truth_flag: bool,
    thresh: WiseCoreThresh = WiseCoreThresh(),
) -> Tuple[float, float, float, bool, int, int]:
    """
    Convenience wrapper:
      - computes N_phase + median(Ḣ) in JAX
      - runs wisecore gate in JAX
      - returns python scalars for host receipt emission

    Returns:
      (N_phase, wuwei_med_Hdot, friend_coherence, truth_flag, verdict_code, fail_code)
    """
    N_phase = phifield_phase_norm(phase_modes)
    Hdot_med = wuwei_median_Hdot(Hdot_series)

    verdict, fail_code = wisecore_gate_jax(
        N_phase=N_phase,
        wuwei_med_Hdot=Hdot_med,
        friend_coherence=jnp.asarray(friend_coherence, dtype=jnp.float32),
        truth_flag=jnp.asarray(truth_flag, dtype=bool),
        thresh_phi_min_N_phase=jnp.asarray(thresh.phi_min_N_phase, dtype=jnp.float32),
        thresh_friend_min_F=jnp.asarray(thresh.friend_min_F, dtype=jnp.float32),
        thresh_require_wuwei=jnp.asarray(thresh.require_wuwei_descent, dtype=bool),
    )

    return (
        float(N_phase),
        float(Hdot_med),
        float(friend_coherence),
        bool(truth_flag),
        int(verdict),
        int(fail_code),
    )
