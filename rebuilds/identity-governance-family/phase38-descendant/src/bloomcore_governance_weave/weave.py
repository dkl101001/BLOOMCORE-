# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import asdict
import math
import statistics

from .model import Proposal, WeaveConfig, WeaveResult
from .receipts import ReceiptChain


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _all_finite(proposal: Proposal) -> bool:
    values = (
        proposal.coherence,
        proposal.fragility,
        proposal.risk,
        proposal.compassion,
        proposal.phase_norm,
        proposal.reflection_fidelity,
        proposal.friend_coherence,
        *proposal.hdot_window,
        *proposal.rgb_drift,
        *proposal.velocity,
        proposal.value_previous,
        proposal.value_current,
        proposal.tau_export,
    )
    return bool(proposal.hdot_window) and all(math.isfinite(float(value)) for value in values)


def _wisdom_audit(proposal: Proposal, cfg: WeaveConfig) -> tuple[float, bool]:
    score = (
        _clamp01(proposal.phase_norm) ** 0.6
        * _clamp01(proposal.reflection_fidelity) ** 0.8
        * _clamp01(proposal.friend_coherence) ** 0.6
    )
    wuwei_ok = statistics.median(proposal.hdot_window) < 0.0
    accepted = (
        score >= cfg.wisdom_threshold
        and wuwei_ok
        and proposal.truth_signal
        and proposal.friend_coherence >= cfg.friend_floor
    )
    return float(score), bool(accepted)


def _veil_audit(proposal: Proposal, cfg: WeaveConfig) -> tuple[float, bool, bool]:
    split = sum(proposal.rgb_drift) / 3.0
    velocity = sum(proposal.velocity) / 3.0
    pressure = split * (0.5 + velocity) * (1.0 - _clamp01(proposal.coherence))
    active = pressure >= cfg.veil_pressure_on
    reanchor = pressure >= cfg.anchor_required_pressure and not proposal.intent_hash
    return float(pressure), bool(active), bool(reanchor)


def _response_vector(proposal: Proposal, veil_active: bool) -> dict[str, float]:
    """Style-only simulation vector; no market action or external operation."""

    uncertainty = _clamp01(0.15 + 0.55 * proposal.fragility + 0.25 * (1.0 - proposal.coherence))
    caution = _clamp01(max(proposal.risk, uncertainty))
    return {
        "recomposition_preference": _clamp01(0.45 + 0.35 * proposal.fragility + (0.15 if veil_active else 0.0)),
        "reflection_preference": _clamp01(0.40 + 0.40 * caution),
        "expression_restraint": _clamp01(0.25 + 0.65 * caution),
        "compassion_presence": _clamp01(proposal.compassion),
    }


def evaluate(
    proposal: Proposal,
    *,
    cfg: WeaveConfig = WeaveConfig(),
    receipts: ReceiptChain | None = None,
) -> WeaveResult:
    """Audit one proposal without executing its content or mutating native state."""

    finite = _all_finite(proposal)
    wisdom_score, wisdom_gate = _wisdom_audit(proposal, cfg) if finite else (0.0, False)
    veil_pressure, veil_active, reanchor = _veil_audit(proposal, cfg) if finite else (math.inf, True, True)
    anti_closure = bool(
        finite
        and proposal.value_current - proposal.value_previous < -cfg.closure_value_eps
        and proposal.tau_export <= cfg.closure_export_eps
    )
    critic_veto = bool(finite and proposal.risk >= cfg.risk_veto_threshold)

    reasons: list[str] = []
    if not finite:
        reasons.append("INPUT.NONFINITE_OR_EMPTY_WINDOW")
    if not proposal.truth_signal:
        reasons.append("TRUTH.SIGNAL_FALSE")
    if anti_closure:
        reasons.append("ANTI_CLOSURE.UNEXPLAINED_CONTRACTION")
    if critic_veto:
        reasons.append("CRITIC.RISK_VETO")
    if proposal.compassion < cfg.compassion_floor:
        reasons.append("COMPASSION.BELOW_EXPRESSION_FLOOR")
    if not wisdom_gate:
        reasons.append("WISDOM.GATE_NOT_MET")
    if reanchor:
        reasons.append("VEIL.INTENT_REANCHOR_REQUIRED")

    hard_stop = (not finite) or (not proposal.truth_signal) or anti_closure or critic_veto
    if hard_stop:
        status = "SUPPRESS_EXPRESSION"
    elif reanchor or not wisdom_gate or proposal.compassion < cfg.compassion_floor:
        status = "DEFER_REANCHOR"
    else:
        status = "ADMIT_EXPRESSION"

    # RSS lineage is represented only as a post-hoc, advisory trace-completeness
    # witness. It never decides status, identity, credibility, worth, or truth.
    trace_facts = (
        bool(proposal.proposal_id),
        bool(proposal.intent_hash),
        bool(proposal.hdot_window),
        finite,
    )
    advisory_trace_quality = sum(trace_facts) / len(trace_facts)

    result = WeaveResult(
        proposal_id=proposal.proposal_id,
        status=status,
        reason_codes=tuple(reasons),
        critic_veto=critic_veto,
        anti_closure_violation=anti_closure,
        wisdom_gate=wisdom_gate,
        veil_active=veil_active,
        reanchor_requested=reanchor,
        advisory_trace_quality=float(advisory_trace_quality),
        wisdom_score=wisdom_score,
        veil_pressure=veil_pressure,
        response_vector=_response_vector(proposal, veil_active),
    )
    if receipts is not None:
        receipts.append(
            "GOVERNANCE_WEAVE.WITNESS.v1",
            {
                **asdict(result),
                "reason_codes": list(result.reason_codes),
                "source_proposal_content_sha256": __import__("hashlib").sha256(
                    proposal.content.encode("utf-8")
                ).hexdigest(),
            },
        )
    return result
