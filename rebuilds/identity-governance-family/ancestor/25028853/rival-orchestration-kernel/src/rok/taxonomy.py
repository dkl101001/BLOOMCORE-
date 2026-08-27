# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class ReasonCodeMeta:
    code: str
    title: str
    description: str

# Minimal reason-code taxonomy (expand as needed)
REASON_CODES: Dict[str, ReasonCodeMeta] = {
    "ASSUMPTION.MISSING": ReasonCodeMeta("ASSUMPTION.MISSING", "Missing assumption", "Plan relies on an unstated or invalid assumption."),
    "CONSTRAINT.OMITTED": ReasonCodeMeta("CONSTRAINT.OMITTED", "Constraint omitted", "Plan omits a required constraint or guardrail."),
    "VERIFICATION.WEAK": ReasonCodeMeta("VERIFICATION.WEAK", "Weak verification", "Plan lacks verification steps or checks."),
    "OBJECTIVE.COLLAPSE": ReasonCodeMeta("OBJECTIVE.COLLAPSE", "Objective collapse", "Plan optimizes one objective while violating secondary requirements."),
}
