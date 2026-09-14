# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


DecisionStatus = Literal[
    "ADMIT_EXPRESSION",
    "DEFER_REANCHOR",
    "SUPPRESS_EXPRESSION",
]


@dataclass(frozen=True)
class WeaveConfig:
    """Thresholds for a bounded expression audit, never identity authority."""

    risk_veto_threshold: float = 0.60
    compassion_floor: float = 0.70
    wisdom_threshold: float = 0.62
    friend_floor: float = 0.30
    veil_pressure_on: float = 0.42
    anchor_required_pressure: float = 0.50
    closure_value_eps: float = 1e-8
    closure_export_eps: float = 1e-8


@dataclass(frozen=True)
class Proposal:
    """Local candidate for expression; content is never executed by this package."""

    proposal_id: str
    content: str
    coherence: float
    fragility: float
    risk: float
    compassion: float
    phase_norm: float
    reflection_fidelity: float
    friend_coherence: float
    truth_signal: bool
    hdot_window: tuple[float, ...]
    rgb_drift: tuple[float, float, float]
    velocity: tuple[float, float, float]
    intent_hash: str
    value_previous: float
    value_current: float
    tau_export: float


@dataclass(frozen=True)
class WeaveResult:
    proposal_id: str
    status: DecisionStatus
    reason_codes: tuple[str, ...]
    critic_veto: bool
    anti_closure_violation: bool
    wisdom_gate: bool
    veil_active: bool
    reanchor_requested: bool
    advisory_trace_quality: float
    wisdom_score: float
    veil_pressure: float
    response_vector: dict[str, float]
    permissions: str = "non_executable"
    authority: str = "NONE"
    canonical_status: str = "PROPOSED_BOUNDED_DESCENDANT"
