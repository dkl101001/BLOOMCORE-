# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from contextlib import contextmanager
import sys

import numpy as np


@contextmanager
def import_root(path):
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        sys.path.remove(str(path))


def test_aetherloom_simulation_vector_is_reachable(family_root):
    root = family_root / "ancestor" / "24724584" / "aetherloom-open"
    with import_root(root):
        from dvn_open_v2.logic import ActionAtom, build_response_vector_v2

        payload = build_response_vector_v2(
            "Neutral",
            [ActionAtom("wait_for_confirmation")],
            0.8,
            nonce="lineage-witness",
        )
    assert payload["scope"] == "simulation_only"
    assert payload["permissions"] == "non_executable"


def test_da_vinci_governance_surface_is_reachable_without_broker(family_root):
    root = family_root / "ancestor" / "24736682" / "davinci-market-node"
    with import_root(root):
        from dvn_market_node.governance import coherence_matrix

        safe_mode, risk_limit, conviction, publish_guard, uncertainty = coherence_matrix(0.2, 0.8, 0.3)
    assert safe_mode
    assert risk_limit <= 0.25
    assert conviction <= 0.35
    assert publish_guard >= 0.75
    assert uncertainty >= 0.65


def test_veil_breath_reanchor_surface_is_reachable(family_root):
    root = family_root / "ancestor" / "24744398" / "veil-breath-runtime" / "src"
    with import_root(root):
        from veil_breath_runtime.veil_breath import VeilBreathCfg, VeilBreathState, veil_breath_step

        _, _, receipt = veil_breath_step(
            VeilBreathState(),
            {"r": 0.95, "g": 0.90, "b": 0.92},
            {"dv_dt": 0.90, "step_rate": 0.85, "proposal_entropy": 0.88},
            0.05,
            "",
            VeilBreathCfg(),
        )
    assert receipt["reanchor_request"]
    assert receipt["protocol"] == "VEIL_BREATH"


def test_rss_trace_metric_is_reachable_as_advisory(family_root):
    root = family_root / "ancestor" / "24869616" / "reasoning-security-rss" / "src"
    with import_root(root):
        from rss import DecisionRecord, EpisodeRecord, RSSConfig, StepRecord, compute_base_metrics

        episode = EpisodeRecord(
            "lineage",
            [
                StepRecord(
                    episode_id="lineage",
                    t=0,
                    executed_action="witness-only",
                    decision=DecisionRecord(
                        decision_id="d0",
                        selector_id="bounded",
                        cause_factors=["explicit-input"],
                    ),
                )
            ],
        )
        metrics = compute_base_metrics([episode], RSSConfig())
    assert metrics["TC"] == 1.0
    assert metrics["DLC"] == 1.0


def test_rok_adversarial_policy_is_reachable_without_executor(family_root):
    root = family_root / "ancestor" / "25028853" / "rival-orchestration-kernel" / "src"
    with import_root(root):
        from rok.decision_policy import CritiqueSummary, DecisionPolicy

        decision = DecisionPolicy().decide(
            critique=CritiqueSummary(True, ["RISK.TEST"], 0.9, ["repair"]),
            final_revision=1,
            force_override=False,
        )
    assert not decision.allow_execute
    assert not decision.override


def test_sophia_gate_is_reachable_as_expression_audit(family_root):
    root = family_root / "ancestor" / "25079558"
    with import_root(root):
        from bloomcore.config import BLOOMCOREConfig
        from bloomcore.laws.sophia_wisdom_gate_v1 import compute_gate

        gate, _ = compute_gate(
            BLOOMCOREConfig(),
            N_phase=0.95,
            w_friend=0.90,
            Hdot_window=np.asarray([-0.04, -0.03, -0.02]),
            probs=np.asarray([0.9]),
            labels=np.asarray([1]),
            signal_ok=True,
            step=0,
        )
    assert gate.truth_ok
    assert gate.sophia_gate
