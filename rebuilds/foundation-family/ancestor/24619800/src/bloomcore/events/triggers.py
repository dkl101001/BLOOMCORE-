from __future__ import annotations

from typing import Any, Dict, Optional


def trigger_cluster_leak(cluster_id: str, iso_score: float, threshold: float) -> Optional[Dict[str, Any]]:
    """Emit a CLUSTER_LEAK event when iso_score < threshold."""
    if iso_score < threshold:
        return {"type": "CLUSTER_LEAK", "cluster_id": cluster_id, "iso": float(iso_score)}
    return None


def trigger_global_fracture(F_net: float, threshold: float) -> Optional[Dict[str, Any]]:
    """Emit a GLOBAL_FRACTURE event when network fracture exceeds threshold."""
    if F_net > threshold:
        return {"type": "GLOBAL_FRACTURE", "F_net": float(F_net)}
    return None
