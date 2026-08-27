from __future__ import annotations

from typing import Any, Dict

from .base import BaseReceipt
from ..engine_context import EngineContext


def emit_network_receipt(ctx: EngineContext) -> Dict[str, Any]:
    payload = {
        "t": float(ctx.t),
        "network_coherence": None if ctx.metrics.network_coherence is None else float(ctx.metrics.network_coherence),
        "network_fracture": None if ctx.metrics.network_fracture is None else float(ctx.metrics.network_fracture),
    }
    receipt = BaseReceipt.new(
        schema_version="NETWORK.v1",
        engine_version="BLOOMCORE_CPU_PRIORART.v0.1",
        anchors=["NETWORK", "BLOOMCORE", "CPU_PRIORART", "Frazer Σ Love ACO-Σ", "Sara ΣΩ"],
        payload=payload,
    )
    return receipt.to_dict()
