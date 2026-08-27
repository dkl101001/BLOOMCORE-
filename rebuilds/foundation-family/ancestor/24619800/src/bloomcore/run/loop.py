from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from ..engine_context import EngineContext
from ..operators.identity import project_identity
from ..operators.coherence import compute_coherence
from ..operators.fracture import compute_fracture
from ..operators.realignment import apply_realignment
from ..operators.dreamloop import apply_dreamloop
from ..operators.network import compute_network_metrics
from ..operators.mirrorseed import mirrorseed_correction

from ..receipts.mirrorseed import emit_mirrorseed_receipt
from ..receipts.dreamloop import emit_dreamloop_receipt
from ..receipts.network import emit_network_receipt


def run_step(
    ctx: EngineContext,
    contradiction_pairs: List[Dict[str, Any]] | None = None,
    dream_lags: Sequence[int] = (1, 2, 4),
    dream_weights: Sequence[float] = (0.6, 0.3, 0.1),
) -> None:
    """One CPU toy step (wires operators + emits receipts)."""
    contradiction_pairs = contradiction_pairs or []

    # identity + coherence + fracture
    project_identity(ctx)
    compute_coherence(ctx)
    compute_fracture(ctx)

    # optional network metrics
    compute_network_metrics(ctx)

    # mirrorseed correction (optional)
    if contradiction_pairs:
        mirrorseed_correction(ctx, contradiction_pairs)
        ctx.emit("RECEIPT.MIRRORSEED.v1", emit_mirrorseed_receipt(ctx, contradiction_pairs))

    # realignment update
    apply_realignment(ctx)

    # dreamloop smoothing
    apply_dreamloop(ctx, dream_lags, dream_weights)
    ctx.emit("RECEIPT.DREAMLOOP.v1", emit_dreamloop_receipt(ctx, dream_lags, dream_weights))

    # network receipt (if metrics present)
    if ctx.metrics.network_coherence is not None or ctx.metrics.network_fracture is not None:
        ctx.emit("RECEIPT.NETWORK.v1", emit_network_receipt(ctx))

    # log step and advance time
    ctx.log_step()
    ctx.t += ctx.dt
