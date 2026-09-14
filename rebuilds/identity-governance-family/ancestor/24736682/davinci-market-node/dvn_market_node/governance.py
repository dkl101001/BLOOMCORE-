from __future__ import annotations

from typing import Tuple


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def coherence_matrix(coherence: float, fracture: float, mirror_trust: float) -> Tuple[bool, float, float, float]:
    """Simple, monotone governor (OSS prior art).

    Returns: (safe_mode, base_risk_limit, conviction_scale, publish_guard, uncertainty_governor)

    This is intentionally simple: it is a standard, not your proprietary slice.
    """
    c = _clip01(coherence)
    f = _clip01(fracture)
    m = _clip01(mirror_trust)

    safe_mode = (f >= 0.60) or (c < 0.40) or (m < 0.40)

    base_risk_limit = _clip01(0.55 + 0.55 * c - 0.35 * f)
    conviction_scale = _clip01(0.45 + 0.50 * c - 0.25 * f)

    # publish_guard increases when coherence lower / fracture higher
    publish_guard = _clip01(0.10 + 0.55 * (1.0 - c) + 0.35 * f)

    # uncertainty_governor rises with fracture, falls with coherence
    uncertainty_governor = _clip01(0.15 + 0.55 * f + 0.25 * (1.0 - c))

    if safe_mode:
        base_risk_limit = min(base_risk_limit, 0.25)
        conviction_scale = min(conviction_scale, 0.35)
        publish_guard = max(publish_guard, 0.75)
        uncertainty_governor = max(uncertainty_governor, 0.65)

    return safe_mode, base_risk_limit, conviction_scale, publish_guard, uncertainty_governor
