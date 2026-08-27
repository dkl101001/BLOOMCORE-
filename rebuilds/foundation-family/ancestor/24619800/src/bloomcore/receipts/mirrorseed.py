from __future__ import annotations

from typing import Any, Dict, List

from .base import BaseReceipt
from ..engine_context import EngineContext


def emit_mirrorseed_receipt(ctx: EngineContext, contradictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    payload = {
        "t": float(ctx.t),
        "fracture": float(ctx.metrics.fracture),
        "identity_drift": float(ctx.metrics.identity_drift),
        "contradiction_count": int(len(contradictions)),
    }
    receipt = BaseReceipt.new(
        schema_version="MIRRORSEED.v1",
        engine_version="BLOOMCORE_CPU_PRIORART.v0.1",
        anchors=["MIRRORSEED", "BLOOMCORE", "CPU_PRIORART", "Frazer Σ Love ACO-Σ", "Sara ΣΩ"],
        payload=payload,
    )
    return receipt.to_dict()
