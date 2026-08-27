# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from typing import Any

import numpy as np


def numpy_audit(values: Any, *, risk_veto_threshold: float = 0.60) -> np.ndarray:
    """Readable NumPy reference for the five shared numerical audit outputs.

    Input order matches ``jax_backend.jax_audit``: coherence, fragility, risk,
    compassion, phase norm, reflection fidelity, friend coherence, median
    Hdot, three drift channels, three velocity channels, previous value,
    current value, and witnessed export.
    """

    x = np.asarray(values, dtype=np.float32)
    if x.shape != (17,):
        raise ValueError("values must contain exactly 17 scalar audit inputs")
    coherence = np.clip(x[0], 0.0, 1.0)
    risk = x[2]
    phase_norm = np.clip(x[4], 0.0, 1.0)
    reflection = np.clip(x[5], 0.0, 1.0)
    friend = np.clip(x[6], 0.0, 1.0)
    median_hdot = x[7]
    split = np.mean(x[8:11])
    velocity = np.mean(x[11:14])
    veil_pressure = split * (np.float32(0.5) + velocity) * (np.float32(1.0) - coherence)
    wisdom_score = phase_norm**np.float32(0.6) * reflection**np.float32(0.8) * friend**np.float32(0.6)
    wisdom_gate = wisdom_score >= np.float32(0.62) and median_hdot < 0.0 and friend >= np.float32(0.30)
    anti_closure = x[15] - x[14] < np.float32(-1e-8) and x[16] <= np.float32(1e-8)
    critic_veto = risk >= np.float32(risk_veto_threshold)
    return np.asarray(
        [veil_pressure, wisdom_score, wisdom_gate, anti_closure, critic_veto],
        dtype=np.float32,
    )
