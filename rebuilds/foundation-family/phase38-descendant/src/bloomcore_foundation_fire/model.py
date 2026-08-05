# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple

import numpy as np


class FireConfig(NamedTuple):
    """Shared numerical contract for the oracle and JAX descendant."""

    field_dt: float = 0.02
    diffusion: float = 0.08
    decay: float = 0.15
    eta: float = 0.05
    sigma_smooth: float = 0.25
    kcut: float = 5.0
    domain_half_extent: float = 8.0
    chiral_mix: float = 0.60
    force_alpha0: float = 1.20
    force_max: float = 4.50
    noise_scale: float = 0.0
    bloom_grad_gain: float = 0.05
    bloom_dtau_gain: float = 0.10
    bloom_force_max: float = 0.25
    identity_alpha: float = 0.90
    realign_alpha: float = 0.10
    realign_beta: float = 0.01
    fracture_grad_scale: float = 1.0
    dream_gamma: float = 0.05
    memory_alpha: float = 0.25
    fracture_eta: float = 1e-6
    phi_min: float = 0.20
    friend_min: float = 0.30
    require_wuwei: bool = True


class FireMetrics(NamedTuple):
    coherence: Any
    fracture: Any
    identity_drift: Any
    phase_norm: Any
    hdot_median: Any
    friend_coherence: Any
    bloom_force: Any
    verdict: Any
    fail_code: Any
    sentinel_allowed: Any


@dataclass
class OracleState:
    tick: int
    vector: np.ndarray
    previous: np.ndarray
    identity: np.ndarray
    field: np.ndarray
    memory: np.ndarray
    hdot_history: np.ndarray
    energy_prev: np.float32
    topology: np.ndarray
    coupling: np.ndarray
    seed: int


def initial_oracle_state(
    *,
    vector: np.ndarray,
    field: np.ndarray,
    topology: np.ndarray | None = None,
    seed: int = 151,
) -> OracleState:
    vector32 = np.asarray(vector, dtype=np.float32)
    field32 = np.asarray(field, dtype=np.float32)
    n = vector32.shape[0]
    if topology is None:
        topology32 = np.eye(n, dtype=np.float32)
    else:
        topology32 = np.asarray(topology, dtype=np.float32)
    energy = np.float32(np.mean(field32 * field32) + 0.5 * np.mean(vector32 * vector32))
    return OracleState(
        tick=0,
        vector=vector32.copy(),
        previous=vector32.copy(),
        identity=vector32.copy(),
        field=field32.copy(),
        memory=vector32.copy(),
        hdot_history=np.zeros(4, dtype=np.float32),
        energy_prev=energy,
        topology=topology32.copy(),
        coupling=np.ones_like(vector32),
        seed=int(seed),
    )
