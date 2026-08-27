# SPDX-License-Identifier: AGPL-3.0-only
import numpy as np

from bloomcore_foundation_fire.model import FireConfig, initial_oracle_state
from bloomcore_foundation_fire.numpy_oracle import oracle_step, zero_extend_oracle
from bloomcore_foundation_fire.orchestrator import run_oracle_cycle
from bloomcore_foundation_fire.receipts import ReceiptChain


def fixture():
    vector = np.asarray([0.2, -0.1, 0.35, 0.05], dtype=np.float32)
    field = np.linspace(-0.3, 0.3, 64, dtype=np.float32).reshape(8, 8)
    topology = np.asarray(
        [[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 1]],
        dtype=np.float32,
    )
    return vector, field, topology


def test_oracle_receipt_chain_and_topology_payload():
    vector, field, topology = fixture()
    state = initial_oracle_state(vector=vector, field=field, topology=topology)
    chain = ReceiptChain()
    config = FireConfig(phi_min=0.0, require_wuwei=False)
    next_state, metrics, receipt = run_oracle_cycle(
        state,
        drive=np.zeros_like(vector),
        weight=np.eye(vector.size, dtype=np.float32),
        truth_flag=True,
        chain=chain,
        config=config,
    )
    assert chain.verify()
    assert receipt["payload"]["emission"] == "ALLOW"
    assert int(metrics.sentinel_allowed) == 1
    np.testing.assert_array_equal(next_state.topology, topology)


def test_zero_extension_recovery_preserves_base_transition():
    vector, field, topology = fixture()
    state = initial_oracle_state(vector=vector, field=field, topology=topology)
    extended = zero_extend_oracle(state, 3)
    config = FireConfig(phi_min=0.0, require_wuwei=True)
    for _ in range(5):
        state, base_metrics = oracle_step(
            state,
            drive=np.zeros(4, dtype=np.float32),
            weight=np.eye(4, dtype=np.float32),
            truth_flag=True,
            config=config,
        )
        extended, extended_metrics = oracle_step(
            extended,
            drive=np.zeros(7, dtype=np.float32),
            weight=np.pad(np.eye(4, dtype=np.float32), ((0, 3), (0, 3))),
            truth_flag=True,
            config=config,
        )
        np.testing.assert_allclose(extended.vector[:4], state.vector, atol=1e-6)
        np.testing.assert_allclose(extended.previous[:4], state.previous, atol=1e-6)
        np.testing.assert_allclose(extended.identity[:4], state.identity, atol=1e-6)
        np.testing.assert_allclose(extended.memory[:4], state.memory, atol=1e-6)
        np.testing.assert_allclose(extended.field, state.field, atol=1e-6)
        np.testing.assert_allclose(extended.hdot_history, state.hdot_history, atol=1e-6)
        np.testing.assert_allclose(extended.energy_prev, state.energy_prev, atol=1e-6)
        np.testing.assert_allclose(
            np.asarray(extended_metrics[:-3], dtype=np.float32),
            np.asarray(base_metrics[:-3], dtype=np.float32),
            atol=1e-6,
        )
        np.testing.assert_array_equal(extended_metrics[-3:], base_metrics[-3:])
    np.testing.assert_array_equal(extended.topology[:4, :4], topology)
    np.testing.assert_array_equal(extended.topology[4:, :], 0)
    np.testing.assert_array_equal(extended.topology[:, 4:], 0)


def test_topology_is_explicitly_inert_in_this_descendant():
    vector, field, _ = fixture()
    identity = initial_oracle_state(
        vector=vector, field=field, topology=np.eye(4, dtype=np.float32)
    )
    dense = initial_oracle_state(
        vector=vector, field=field, topology=np.ones((4, 4), dtype=np.float32)
    )
    config = FireConfig(phi_min=0.0, require_wuwei=False)
    identity_next, identity_metrics = oracle_step(
        identity,
        drive=np.zeros(4, dtype=np.float32),
        weight=np.eye(4, dtype=np.float32),
        truth_flag=True,
        config=config,
    )
    dense_next, dense_metrics = oracle_step(
        dense,
        drive=np.zeros(4, dtype=np.float32),
        weight=np.eye(4, dtype=np.float32),
        truth_flag=True,
        config=config,
    )
    np.testing.assert_array_equal(identity_next.vector, dense_next.vector)
    np.testing.assert_array_equal(identity_next.field, dense_next.field)
    assert identity_metrics == dense_metrics
    assert not np.array_equal(identity_next.topology, dense_next.topology)
