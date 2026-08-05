# SPDX-License-Identifier: AGPL-3.0-only
import sys
from pathlib import Path

import numpy as np


FAMILY = Path(__file__).resolve().parents[2]


def add(path: Path):
    sys.path.insert(0, str(path))


def test_bloomforce_contract_is_reachable():
    add(FAMILY / "ancestor" / "24621318" / "src")
    from bloomforce_core.engine import compute_bloomforce
    from bloomforce_core.types import BloomforceParams, ObsBundle

    value = compute_bloomforce(
        BloomforceParams(dtau_gain=0.1, grad_rho_gain=0.05, max_force_norm=0.25),
        ObsBundle(psi_rho=0.0, grad_rho=0.4, delta_tau_mass=0.2),
    )
    assert np.isclose(value, 0.04)


def test_cpu_toy_and_sentinel_kernel_are_reachable():
    add(FAMILY / "ancestor" / "24619800" / "src")
    from bloomcore.engine_context import EngineContext
    from bloomcore.operators.coherence import compute_coherence
    from bloomcore.xp_backend import XPBackend

    context = EngineContext(xp_backend=XPBackend())
    context.state["S"] = np.asarray([1.0, 2.0])
    context.params["W"] = np.eye(2)
    compute_coherence(context)
    assert context.metrics.coherence == 5.0

    add(FAMILY / "ancestor" / "24619844" / "sentinel_lite_kernel")
    from sentinel_lite_kernel.core.policy import AllowlistPolicy
    from sentinel_lite_kernel.core.types import ProposedCommand

    policy = AllowlistPolicy("foundation", ["public"], ["emit"], [], [], 1024)
    decision = policy.decide(ProposedCommand("id", "public", "emit", {}, []))
    assert decision.allowed


def test_continuity_and_world_receipt_surfaces_are_reachable(tmp_path):
    add(FAMILY / "ancestor" / "24619824" / "bloomcore-continuity-spine" / "src")
    from bloomcore_spine.continuity_spine import ContinuitySpine

    spine = ContinuitySpine()
    spine.hook("BLOOMCORE.FIELD_PULSE.v1", {"source_id": "foundation", "tick": 1})
    assert spine.compute_invariants().tick == 1

    add(FAMILY / "ancestor" / "24714760" / "world_engine_ship_safe")
    from world_engine.bloomcore import BLOOMCORE

    ledger = BLOOMCORE(str(tmp_path / "receipts"), str(tmp_path / "chain.jsonl"))
    ledger.log({"dtau_id": "foundation-1", "kind": "TEST"})
    assert ledger.verify()["status"] == "INTACT"
