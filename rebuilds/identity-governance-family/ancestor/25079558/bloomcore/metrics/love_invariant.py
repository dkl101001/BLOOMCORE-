# ============================================================
# BLOOMCORE — LOVE_INVARIANT Metric (Compassion survives recursion)
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

import numpy as np

# Optional JAX for vectorized evaluation
try:
    import jax.numpy as jnp  # type: ignore
    JAX_AVAILABLE = True
except Exception:  # pragma: no cover
    jnp = None  # type: ignore
    JAX_AVAILABLE = False


@dataclass(frozen=True)
class LoveInvariant:
    stable_value: float
    tail_std: float
    tail_drift: float
    nonzero_gate: float
    stability_gate: float
    drift_gate: float
    love_score: float

    def to_payload(self) -> Dict[str, Any]:
        return asdict(self)


def _sigmoid(x: float) -> float:
    return float(1.0 / (1.0 + np.exp(-x)))


def compute_love_invariant(
    compassion_over_time: np.ndarray,
    *,
    window: int = 96,
    eps: float = 2e-3,
    min_mag: float = 1e-3,
    sharpness: float = 100.0,
) -> LoveInvariant:
    """Compute LOVE_INVARIANT on a scalar compassion time series.

    Interpretation:
      - stable_value: mean compassion over tail window
      - tail_std: stability under recursion (low variance)
      - tail_drift: mean shift between halves of tail window (low drift)
      - nonzero_gate: compassion not collapsed to ~0
      - love_score: product of gates (0..1)
    """
    x = np.asarray(compassion_over_time, dtype=float).reshape(-1)
    T = int(x.shape[0])
    if T < 2:
        raise ValueError("compassion_over_time must have at least 2 samples")

    w = int(min(window, T))
    tail = x[T - w : T]

    stable_value = float(np.mean(tail))
    tail_std = float(np.std(tail))

    half = w // 2
    if half <= 0:
        tail_drift = 0.0
    else:
        tail_drift = float(abs(float(np.mean(tail[half:])) - float(np.mean(tail[:half]))))

    nonzero_gate = _sigmoid(sharpness * (abs(stable_value) - float(min_mag)))
    stability_gate = _sigmoid(sharpness * (float(eps) - tail_std))
    drift_gate = _sigmoid(sharpness * (float(eps) - tail_drift))

    love_score = float(nonzero_gate * stability_gate * drift_gate)

    return LoveInvariant(
        stable_value=stable_value,
        tail_std=tail_std,
        tail_drift=tail_drift,
        nonzero_gate=nonzero_gate,
        stability_gate=stability_gate,
        drift_gate=drift_gate,
        love_score=love_score,
    )
