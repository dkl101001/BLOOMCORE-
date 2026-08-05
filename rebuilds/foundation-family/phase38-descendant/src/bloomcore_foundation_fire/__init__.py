# SPDX-License-Identifier: AGPL-3.0-only
"""BLOOMCORE foundation-family Phase 38 descendant.

This package is additive. It does not replace or mutate the preserved ancestors.
"""

from .model import FireConfig, FireMetrics, OracleState, initial_oracle_state
from .numpy_oracle import oracle_rollout, oracle_step, zero_extend_oracle

__all__ = [
    "FireConfig",
    "FireMetrics",
    "OracleState",
    "initial_oracle_state",
    "oracle_rollout",
    "oracle_step",
    "zero_extend_oracle",
]
