from __future__ import annotations

from typing import Any, Dict

from ..engine_context import EngineContext


def severity_cluster_leak(event: Dict[str, Any], ctx: EngineContext) -> float:
    """More negative iso => more severe (toy)."""
    iso_val = float(event.get("iso", 0.0))
    return float(-iso_val)


def severity_cluster_split(event: Dict[str, Any], ctx: EngineContext) -> float:
    iso_val = float(event.get("iso", 0.0))
    return float(-2.0 * iso_val)


def severity_global_fracture(event: Dict[str, Any], ctx: EngineContext) -> float:
    F_net = float(event.get("F_net", 0.0))
    return float(F_net)
