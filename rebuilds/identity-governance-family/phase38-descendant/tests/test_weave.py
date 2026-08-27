# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace

from bloomcore_governance_weave.cli import sample_proposal
from bloomcore_governance_weave.receipts import ReceiptChain
from bloomcore_governance_weave.weave import evaluate


def test_admits_bounded_expression_and_receipts_witness_only():
    chain = ReceiptChain()
    result = evaluate(sample_proposal(), receipts=chain)
    assert result.status == "ADMIT_EXPRESSION"
    assert result.permissions == "non_executable"
    assert result.authority == "NONE"
    assert chain.verify()


def test_risk_veto_suppresses_expression():
    result = evaluate(replace(sample_proposal(), risk=0.91))
    assert result.status == "SUPPRESS_EXPRESSION"
    assert result.critic_veto
    assert "CRITIC.RISK_VETO" in result.reason_codes


def test_unexplained_contraction_is_audit_violation():
    result = evaluate(replace(sample_proposal(), value_current=0.5, tau_export=0.0))
    assert result.status == "SUPPRESS_EXPRESSION"
    assert result.anti_closure_violation


def test_explicit_export_prevents_false_anti_closure_violation():
    result = evaluate(replace(sample_proposal(), value_current=0.5, tau_export=0.5))
    assert result.status == "ADMIT_EXPRESSION"
    assert not result.anti_closure_violation


def test_veil_requests_reanchor_without_bound_intent():
    result = evaluate(
        replace(
            sample_proposal(),
            coherence=0.05,
            rgb_drift=(0.95, 0.90, 0.92),
            velocity=(0.90, 0.85, 0.88),
            intent_hash="",
        )
    )
    assert result.status == "DEFER_REANCHOR"
    assert result.reanchor_requested
    assert "VEIL.INTENT_REANCHOR_REQUIRED" in result.reason_codes


def test_trace_advisory_never_overrides_truth_failure():
    result = evaluate(replace(sample_proposal(), truth_signal=False))
    assert result.advisory_trace_quality == 1.0
    assert result.status == "SUPPRESS_EXPRESSION"


def test_empty_wuwei_window_is_invalid_not_an_exception():
    result = evaluate(replace(sample_proposal(), hdot_window=()))
    assert result.status == "SUPPRESS_EXPRESSION"
    assert "INPUT.NONFINITE_OR_EMPTY_WINDOW" in result.reason_codes
