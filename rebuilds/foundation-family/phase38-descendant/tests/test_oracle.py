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


def test_oracle_receipt_chain_and_topology():
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
    config = FireConfig(phi_min=0.0, require_wuwei=False)
    base_next, _ = oracle_step(
        state,
        drive=np.zeros(4, dtype=np.float32),
        weight=np.eye(4, dtype=np.float32),
        truth_flag=True,
        config=config,
    )
    extended_next, _ = oracle_step(
        extended,
        drive=np.zeros(7, dtype=np.float32),
        weight=np.pad(np.eye(4, dtype=np.float32), ((0, 3), (0, 3))),
        truth_flag=True,
        config=config,
    )
    np.testing.assert_allclose(extended_next.vector[:4], base_next.vector, atol=1e-6)
    np.testing.assert_allclose(extended_next.field, base_next.field, atol=1e-6)
    np.testing.assert_array_equal(extended_next.topology[:4, :4], topology)
    np.testing.assert_array_equal(extended_next.topology[4:, :], 0)
    np.testing.assert_array_equal(extended_next.topology[:, 4:], 0)
