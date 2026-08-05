# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from typing import Any

import numpy as np

from .model import FireConfig, FireMetrics, OracleState
from .numpy_oracle import oracle_step
from .receipts import ReceiptChain


LINEAGE_STAGES = (
    "BLOOMFORCE force contract",
    "WISECORE emission membrane",
    "BLOOMCORE pseudo-spectral carrier",
    "Sentinel LITE allowlist decision",
    "Continuity Spine telemetry boundary",
    "CPU Toy identity/coherence/fracture oracle",
    "World Engine receipt persistence",
)


def metrics_payload(metrics: FireMetrics) -> dict[str, Any]:
    return {
        name: value.item() if hasattr(value, "item") else value
        for name, value in metrics._asdict().items()
    }


def run_oracle_cycle(
    state: OracleState,
    *,
    drive: np.ndarray,
    weight: np.ndarray,
    truth_flag: bool,
    chain: ReceiptChain,
    config: FireConfig = FireConfig(),
) -> tuple[OracleState, FireMetrics, dict[str, Any]]:
    next_state, metrics = oracle_step(
        state,
        drive=drive,
        weight=weight,
        truth_flag=truth_flag,
        config=config,
    )
    receipt = chain.append(
        "BLOOMCORE.FOUNDATION_FIRE_STEP.v1",
        {
            "tick": int(next_state.tick),
            "backend": "ancestral-numpy-oracle",
            "lineage_stages": list(LINEAGE_STAGES),
            "metrics": metrics_payload(metrics),
            "topology_shape": list(next_state.topology.shape),
            "emission": "ALLOW" if int(metrics.sentinel_allowed) else "SUPPRESS",
        },
    )
    return next_state, metrics, receipt


def run_jax_cycle(
    state,
    *,
    drive,
    weight,
    truth_flag,
    chain: ReceiptChain,
    config: FireConfig = FireConfig(),
):
    """Run one Full Fire step while keeping receipts outside the JIT boundary."""

    from .jax_backend import jax_step

    next_state, metrics = jax_step(state, drive, weight, truth_flag, config)
    receipt = chain.append(
        "BLOOMCORE.FOUNDATION_FIRE_STEP.v1",
        {
            "tick": int(next_state.tick.item()),
            "backend": "full-fire-jax",
            "lineage_stages": list(LINEAGE_STAGES),
            "metrics": metrics_payload(metrics),
            "topology_shape": list(next_state.topology.shape),
            "emission": "ALLOW" if int(metrics.sentinel_allowed.item()) else "SUPPRESS",
        },
    )
    return next_state, metrics, receipt
