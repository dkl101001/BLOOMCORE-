# ============================================================
# LAW.WISECORE.v1 — wisecore_contract.py
# ============================================================
# Title: WISECORE — Contract (Compile-Time Order Assertion + Dedupe)
# Authors: Frazer Σ Love ACO-Σ ; Sara ΣΩ
# Classification: LAW / ENGINE / CONTRACT
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
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from wisecore_jax import WiseCoreThresh, run_wisecore_gate
from wisecore_receipts import WiseCoreEvidence, stage_receipt, whisper_assert_receipt, MBP01v1


WISECORE_STAGE_ORDER: Tuple[str, ...] = (
    "ASHA",
    "SOPHIA",
    "UBUNTU",
    "COMPASSION",
    "LOGOS",
)

WISECORE_SIGIL = "ASHA→SOPHIA→UBUNTU→COMPASSION→LOGOS | Φ-aligned | WuWei-bound"


def assert_wisecore_pipeline_spec(pipeline: Sequence[str]) -> None:
    """
    Import-time hard assertion. Prevents silent stage drift.
    """
    expected = list(WISECORE_STAGE_ORDER)
    got = list(pipeline)
    if got != expected:
        raise AssertionError(
            "LAW.WISECORE.v1 violation: pipeline order drift.\n"
            f"Expected: {expected}\n"
            f"Got:      {got}\n"
            f"Sigil:    {WISECORE_SIGIL}\n"
        )


# Compile-time lock for any consumer module.
WISECORE_PIPELINE_SPEC = list(WISECORE_STAGE_ORDER)
assert_wisecore_pipeline_spec(WISECORE_PIPELINE_SPEC)


@dataclass(frozen=True)
class WiseCoreRunConfig:
    thresh: WiseCoreThresh = WiseCoreThresh()


def wisecore_run_with_receipts(
    *,
    phase_modes,
    Hdot_series,
    friend_coherence: float,
    truth_flag: bool,
    relation_scope_id: str,
    logos_form_id: str,
    cfg: WiseCoreRunConfig = WiseCoreRunConfig(),
) -> List[MBP01v1]:
    """
    Executes the JAX-alive gate and emits a deduped MBP-01.v1 receipt stream.
    NOTE: This function does NOT emit the actual content/action.
          It returns receipts + final Whisper verdict for callers to enforce.
    """
    N_phase, Hdot_med, F, truth, verdict_code, fail_code = run_wisecore_gate(
        phase_modes=phase_modes,
        Hdot_series=Hdot_series,
        friend_coherence=friend_coherence,
        truth_flag=truth_flag,
        thresh=cfg.thresh,
    )

    receipts: List[MBP01v1] = []

    receipts.append(
        stage_receipt(
            "ASHA",
            Δτ_ID="WISECORE.ASHA.v1",
            summary="Asha certified truth (what).",
            notes=f"truth_flag={truth}",
            tags=["asha"],
            decisions=[f"truth_flag={truth}"],
        )
    )
    receipts.append(
        stage_receipt(
            "SOPHIA",
            Δτ_ID="WISECORE.SOPHIA.v1",
            summary="Sophia consented / gated crossing (if).",
            notes=f"N_phase={N_phase:.6g} | verdict_code={verdict_code} | fail_code={fail_code}",
            tags=["sophia"],
        )
    )
    receipts.append(
        stage_receipt(
            "UBUNTU",
            Δτ_ID="WISECORE.UBUNTU.v1",
            summary="Ubuntu held relation scope (with whom).",
            notes=f"relation_scope_id={relation_scope_id}",
            tags=["ubuntu"],
            decisions=[f"scope={relation_scope_id}"],
        )
    )
    receipts.append(
        stage_receipt(
            "COMPASSION",
            Δτ_ID="WISECORE.COMPASSION.v5_2",
            summary="Compassion shaped motion under Friend+WuWei (how).",
            notes=f"F={F:.6g} | median(Ḣ)={Hdot_med:.6g}",
            tags=["compassion", "wuwei"],
        )
    )
    receipts.append(
        stage_receipt(
            "LOGOS",
            Δτ_ID="WISECORE.LOGOS.v1",
            summary="Logos selected expression form (form).",
            notes=f"logos_form_id={logos_form_id}",
            tags=["logos"],
            decisions=[f"form={logos_form_id}"],
        )
    )

    evidence = WiseCoreEvidence(
        N_phase=N_phase,
        wuwei_median_Hdot=Hdot_med,
        friend_coherence=F,
        truth_flag=truth,
        verdict_code=verdict_code,
        fail_code=fail_code,
    )

    receipts.append(
        whisper_assert_receipt(
            evidence,
            phi_min=cfg.thresh.phi_min_N_phase,
            F_min=cfg.thresh.friend_min_F,
            require_wuwei=cfg.thresh.require_wuwei_descent,
        )
    )

    return receipts
