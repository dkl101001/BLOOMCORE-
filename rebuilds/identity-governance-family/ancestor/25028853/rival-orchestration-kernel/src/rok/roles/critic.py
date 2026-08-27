# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations
from .base import Plan, Critique
from rok.taxonomy import REASON_CODES

def critique_plan(plan: Plan) -> Critique:
    reasons = []
    risks = []
    objections = []
    requested = []

    # Simple synthetic critic for reference: veto if assumptions are generic and verification is weak.
    # Downstream can swap in model-backed critics.
    if not plan.assumptions or len(plan.assumptions) < 2:
        reasons.append("ASSUMPTION.MISSING")
        objections.append("Plan does not enumerate assumptions.")
        requested.append("Enumerate explicit assumptions.")
    if not any("verification" in s.lower() for s in plan.steps):
        reasons.append("VERIFICATION.WEAK")
        objections.append("Plan lacks explicit verification step.")
        requested.append("Add a verification step or sanity check.")
    veto = len(reasons) > 0
    risk_score = 0.75 if veto else 0.20
    if veto:
        risks.append("Silent failure risk due to missing assumptions/verification.")
    return Critique(
        veto=veto,
        reasons=reasons,
        risks=risks,
        objections=objections,
        requested_changes=requested,
        risk_score=risk_score,
        notes=None,
    )
