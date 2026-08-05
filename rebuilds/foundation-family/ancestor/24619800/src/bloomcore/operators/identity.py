from __future__ import annotations

from ..engine_context import EngineContext


def project_identity(ctx: EngineContext) -> None:
    """Compute a toy identity estimate and identity drift.

    Expects:
      ctx.state["S"]      : array (n,)
      ctx.state["S_prev"] : array (n,)

    Produces:
      ctx.state["I"]      : array (n,)
      ctx.metrics.identity_drift : float
    """
    S = ctx.state["S"]
    S_prev = ctx.state["S_prev"]

    # simple low-pass "identity"
    alpha = float(ctx.params.get("identity_alpha", 0.9))
    I = alpha * S_prev + (1.0 - alpha) * S
    ctx.state["I"] = I

    dI = ctx.xp_backend.norm(I - ctx.state["I_prev"]) if "I_prev" in ctx.state else 0.0
    ctx.metrics.identity_drift = float(dI)
    ctx.state["I_prev"] = I
