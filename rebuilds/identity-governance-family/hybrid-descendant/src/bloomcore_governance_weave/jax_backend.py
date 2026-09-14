# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from typing import Any


def jax_audit(values: Any, *, risk_veto_threshold: float = 0.60) -> Any:
    """JIT-capable numerical audit matching the descendant's shared formulas.

    Input order: coherence, fragility, risk, compassion, phase_norm,
    reflection_fidelity, friend_coherence, median_hdot, drift_r/g/b,
    velocity/dv/entropy, value_previous, value_current, tau_export.
    """

    import jax.numpy as jnp

    x = jnp.asarray(values, dtype=jnp.float32)
    coherence = jnp.clip(x[0], 0.0, 1.0)
    risk = x[2]
    phase_norm = jnp.clip(x[4], 0.0, 1.0)
    reflection = jnp.clip(x[5], 0.0, 1.0)
    friend = jnp.clip(x[6], 0.0, 1.0)
    median_hdot = x[7]
    split = jnp.mean(x[8:11])
    velocity = jnp.mean(x[11:14])
    veil_pressure = split * (0.5 + velocity) * (1.0 - coherence)
    wisdom_score = phase_norm**0.6 * reflection**0.8 * friend**0.6
    wisdom_gate = jnp.logical_and(
        jnp.logical_and(wisdom_score >= 0.62, median_hdot < 0.0),
        friend >= 0.30,
    )
    d_value = x[15] - x[14]
    anti_closure = jnp.logical_and(d_value < -1e-8, x[16] <= 1e-8)
    critic_veto = risk >= risk_veto_threshold
    return jnp.stack(
        (
            veil_pressure,
            wisdom_score,
            wisdom_gate.astype(jnp.float32),
            anti_closure.astype(jnp.float32),
            critic_veto.astype(jnp.float32),
        )
    )


def jitted_jax_audit(values: Any) -> Any:
    import jax

    return jax.jit(jax_audit)(values)
