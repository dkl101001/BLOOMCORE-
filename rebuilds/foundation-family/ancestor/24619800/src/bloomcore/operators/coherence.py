from __future__ import annotations

from ..engine_context import EngineContext


def compute_coherence(ctx: EngineContext) -> None:
    """Compute C(S) = S^T W S.

    Expects:
      ctx.state["S"] : array (n,)
      ctx.params["W"] : array (n,n) PSD-ish (caller responsibility)
    """
    S = ctx.state["S"]
    W = ctx.params["W"]
    C = float(ctx.xp_backend.matmul(S.T, ctx.xp_backend.matmul(W, S)))
    ctx.metrics.coherence = C
