# ============================================================
# Integration Logic
# Title: ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)
# ============================================================
from __future__ import annotations

from typing import Any, Dict
from .logic import build_response_vector_v2, ActionAtom

def wire_open_report(report: Dict[str, Any], context_data: Dict[str, Any], ctx=None) -> Dict[str, Any]:
    signals = context_data.get("signals", {})

    atoms = []
    if signals.get("vol_compression"):
        atoms.append(ActionAtom("wait_for_confirmation"))
        atoms.append(ActionAtom("favor_dispersion_aware_exposure", weight=0.8))

    if signals.get("tail_risk"):
        atoms.append(ActionAtom("increase_hedge_bias", weight=1.0))

    tech_params = {
        "Accumulation": signals.get("accum_target", "None"),
        "Invalidation": signals.get("invalidation_level", "None"),
        "Trigger": signals.get("trigger_cond", "None"),
    }

    mm = report.get("mythmath_core", {}) or {}
    fragility_index = float(context_data.get("fragility_index", mm.get("fragility_index", 0.50)))

    report["response_vector"] = build_response_vector_v2(
        posture=context_data.get("posture", "Neutral"),
        action_atoms=atoms,
        coherence=float(context_data.get("coherence", mm.get("coherence", 0.50))),
        fragility_index=fragility_index,
        technical_params=tech_params,
        ctx=ctx,
        eq_id=report["as_of"]["eq_id"],
    )

    return report
