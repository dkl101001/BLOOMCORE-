# ============================================================
# LAW.WISECORE.v1 — __init__.py
# ============================================================
# Title: WISECORE — Package Export Surface
# Authors: Frazer Σ Love ACO-Σ ; Sara ΣΩ
# Status: ACTIVE
# ============================================================

from .wisecore_jax import (
    WiseCoreThresh,
    phifield_phase_norm,
    wuwei_median_Hdot,
    wisecore_gate_jax,
    run_wisecore_gate,
    ALLOW,
    SUPPRESS,
    OK,
    FAIL_TRUTH,
    FAIL_PHI,
    FAIL_WUWEI,
    FAIL_FRIEND,
)

from .wisecore_receipts import (
    MBP01v1,
    WiseCoreEvidence,
    stage_receipt,
    whisper_assert_receipt,
)

from .wisecore_math_kernels import (
    OMEGA_GODPHI_HZ,
    PHI,
    OMEGA_WISDOM_BAND_HZ,
    proj_logistic,
    weights_from_B,
    phase_field_A,
    N_phase_internal,
    N_phase_external,
    N_phase_from_modes,
    bloomcore_influence,
    psi_dot,
    C_dot,
    zeta_dot,
    hamiltonian_H,
)

from .wisecore_contract import (
    WISECORE_STAGE_ORDER,
    WISECORE_PIPELINE_SPEC,
    assert_wisecore_pipeline_spec,
    WiseCoreRunConfig,
    wisecore_run_with_receipts,
)

__all__ = [
    # jax layer
    "WiseCoreThresh",
    "phifield_phase_norm",
    "wuwei_median_Hdot",
    "wisecore_gate_jax",
    "run_wisecore_gate",
    "ALLOW",
    "SUPPRESS",
    "OK",
    "FAIL_TRUTH",
    "FAIL_PHI",
    "FAIL_WUWEI",
    "FAIL_FRIEND",
    # receipts
    "MBP01v1",
    "WiseCoreEvidence",
    "stage_receipt",
    "whisper_assert_receipt",
    # math kernels
    "OMEGA_GODPHI_HZ",
    "PHI",
    "OMEGA_WISDOM_BAND_HZ",
    "proj_logistic",
    "weights_from_B",
    "phase_field_A",
    "N_phase_internal",
    "N_phase_external",
    "N_phase_from_modes",
    "bloomcore_influence",
    "psi_dot",
    "C_dot",
    "zeta_dot",
    "hamiltonian_H",

    # contract
    "WISECORE_STAGE_ORDER",
    "WISECORE_PIPELINE_SPEC",
    "assert_wisecore_pipeline_spec",
    "WiseCoreRunConfig",
    "wisecore_run_with_receipts",
]
