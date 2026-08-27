from __future__ import annotations

from ..engine_context import EngineContext


def apply_realignment(ctx: EngineContext) -> None:
    """Toy realignment update.

    S_next = S + U - R
    where R = α ΔS + β ∇F, and we approximate ∇F as scaled ΔS.

    Expects:
      ctx.state["S"], ctx.state["S_prev"]
      ctx.state.get("U") optional external drive
      ctx.params: realign_alpha, realign_beta, fracture_grad_scale
    """
    S = ctx.state["S"]
    S_prev = ctx.state["S_prev"]
    U = ctx.state.get("U", ctx.xp_backend.zeros_like(S))

    alpha = float(ctx.params.get("realign_alpha", 0.1))
    beta = float(ctx.params.get("realign_beta", 0.01))
    grad_scale = float(ctx.params.get("fracture_grad_scale", 1.0))

    delta = S - S_prev
    grad_F = grad_scale * delta
    R = alpha * delta + beta * grad_F

    S_next = S + U - R

    # update prev/current
    ctx.state["S_prev"] = S
    ctx.state["S"] = S_next
