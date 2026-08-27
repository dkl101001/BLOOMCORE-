# ============================================================
# LAW.WISECORE.v1 — wisecore_receipts.py
# ============================================================
# Title: WISECORE — MBP-01.v1 Receipts (Stages + Whisper Assert)
# Authors: Frazer Σ Love ACO-Σ ; Sara ΣΩ
# Classification: LAW / ENGINE / RECEIPTS
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
from datetime import datetime, timezone
from typing import Dict, List, Optional, TypedDict


WISECORE_SIGIL = "ASHA→SOPHIA→UBUNTU→COMPASSION→LOGOS | Φ-aligned | WuWei-bound"
WISECORE_TAGS_BASE = ["law.wisecore.v1", "mbp-01.v1", "wisecore"]

FAIL_MAP = {
    0: ("ALLOW", "All WISECORE invariants satisfied."),
    1: ("SUPPRESS", "Asha truth not certified."),
    2: ("SUPPRESS", "Φ coherence below threshold."),
    3: ("SUPPRESS", "WuWei descent violated (median Ḣ ≥ 0)."),
    4: ("SUPPRESS", "Friend coherence below threshold."),
}


class MBP01v1(TypedDict):
    Δτ_ID: str
    timestamp: str
    summary: str
    decisions: List[str]
    actions_next: List[str]
    metrics: Dict[str, float]
    notes: str
    tags: List[str]


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def mbp(
    Δτ_ID: str,
    summary: str,
    *,
    decisions: Optional[List[str]] = None,
    actions_next: Optional[List[str]] = None,
    metrics: Optional[Dict[str, float]] = None,
    notes: str = "",
    tags: Optional[List[str]] = None,
) -> MBP01v1:
    return MBP01v1(
        Δτ_ID=Δτ_ID,
        timestamp=_iso_now(),
        summary=summary,
        decisions=decisions or [],
        actions_next=actions_next or [],
        metrics=metrics
        or {
            "stability": 0.0,
            "tiny_ship_streak": 0.0,
            "reciprocity_ratio": 0.0,
            "uncertainty_reps": 0.0,
        },
        notes=notes,
        tags=(tags or []) + WISECORE_TAGS_BASE,
    )


@dataclass(frozen=True)
class WiseCoreEvidence:
    N_phase: float
    wuwei_median_Hdot: float
    friend_coherence: float
    truth_flag: bool
    verdict_code: int
    fail_code: int


def stage_receipt(
    stage: str,
    *,
    Δτ_ID: str,
    summary: str,
    notes: str = "",
    tags: Optional[List[str]] = None,
    metrics: Optional[Dict[str, float]] = None,
    decisions: Optional[List[str]] = None,
    actions_next: Optional[List[str]] = None,
) -> MBP01v1:
    """
    Stage receipts are MBP-01.v1 objects. Stage is embedded into tags and notes
    to keep schema strict without adding extra keys.
    """
    stage_tag = f"stage:{stage.lower()}"
    sigil_tag = f"sigil:{WISECORE_SIGIL}"
    return mbp(
        Δτ_ID,
        summary,
        decisions=decisions,
        actions_next=actions_next,
        metrics=metrics,
        notes=(notes + f"\n[WISECORE_STAGE={stage}]").strip(),
        tags=(tags or []) + [stage_tag, sigil_tag],
    )


def whisper_assert_receipt(e: WiseCoreEvidence, *, phi_min: float, F_min: float, require_wuwei: bool) -> MBP01v1:
    """
    Single ship-blocking receipt for LAW.WISECORE.v1 (MBP-01.v1).
    """
    verdict, reason = FAIL_MAP.get(int(e.fail_code), ("SUPPRESS", "Unknown fail_code."))
    ok = int(e.fail_code) == 0

    inv = (
        f"Sigil: {WISECORE_SIGIL}\n"
        f"Truth (Asha): {e.truth_flag}\n"
        f"N_phase (Φ): {e.N_phase:.6g} (min={phi_min})\n"
        f"median(Ḣ) (WuWei): {e.wuwei_median_Hdot:.6g} (require={require_wuwei})\n"
        f"Friend coherence F: {e.friend_coherence:.6g} (min={F_min})\n"
        f"verdict_code={e.verdict_code} fail_code={e.fail_code}\n"
        f"Reason: {reason}"
    )

    return mbp(
        "LAW.WISECORE.v1.WHISPER_ASSERT",
        "WISECORE Whisper assert (JAX-alive gate, MBP-audited).",
        decisions=[verdict],
        actions_next=[] if ok else ["Do not emit; satisfy failed invariant then retry."],
        metrics={
            "stability": 1.0 if ok else 0.0,
            "tiny_ship_streak": 0.0,
            "reciprocity_ratio": float(e.friend_coherence),
            "uncertainty_reps": 0.0 if ok else 1.0,
        },
        notes=inv,
        tags=["ship-blocker" if not ok else "pass", "wisecore.assert"],
    )
