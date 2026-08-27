# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass(frozen=True)
class Decision:
    allow_execute: bool
    override: bool
    final_revision: int
    reason: str
    reason_codes: List[str]

@dataclass(frozen=True)
class CritiqueSummary:
    veto: bool
    reasons: List[str]
    risk_score: float
    requested_changes: List[str]

@dataclass(frozen=True)
class DecisionPolicy:
    """
    Multi-criteria decision policy.

    Defaults are conservative: veto if critic vetoes above threshold.
    Override is only enabled if explicitly requested by operator.
    """
    risk_veto_threshold: float = 0.60

    def decide(self, *, critique: CritiqueSummary, final_revision: int, force_override: bool) -> Decision:
        if critique.veto and critique.risk_score >= self.risk_veto_threshold and not force_override:
            return Decision(
                allow_execute=False,
                override=False,
                final_revision=final_revision,
                reason="Critic veto (risk above threshold) and no override.",
                reason_codes=list(critique.reasons),
            )
        if critique.veto and force_override:
            return Decision(
                allow_execute=True,
                override=True,
                final_revision=final_revision,
                reason="Override forced despite critic veto.",
                reason_codes=list(critique.reasons),
            )
        return Decision(
            allow_execute=True,
            override=False,
            final_revision=final_revision,
            reason="Cleared by policy.",
            reason_codes=list(critique.reasons),
        )
