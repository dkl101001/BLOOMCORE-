from __future__ import annotations

from typing import Any, Dict, Sequence

from .base import BaseReceipt
from ..engine_context import EngineContext


def emit_dreamloop_receipt(ctx: EngineContext, lags: Sequence[int], weights: Sequence[float]) -> Dict[str, Any]:
    payload = {
        "t": float(ctx.t),
        "dream_gamma": float(ctx.params.get("dream_gamma", 0.0)),
        "lags": [int(x) for x in lags],
        "weights": [float(w) for w in weights],
    }
    receipt = BaseReceipt.new(
        schema_version="DREAMLOOP.v1",
        engine_version="BLOOMCORE_CPU_PRIORART.v0.1",
        anchors=["DREAMLOOP", "BLOOMCORE", "CPU_PRIORART", "Frazer Σ Love ACO-Σ", "Sara ΣΩ"],
        payload=payload,
    )
    return receipt.to_dict()
