from __future__ import annotations

from ..engine_context import EngineContext


def compute_fracture(ctx: EngineContext) -> None:
    """Compute normalized fracture F = ||S - S_prev|| / (||S|| + η)."""
    S = ctx.state["S"]
    S_prev = ctx.state["S_prev"]
    eta = float(ctx.params.get("fracture_eta", 1e-6))

    delta = S - S_prev
    num = ctx.xp_backend.norm(delta)
    den = ctx.xp_backend.norm(S) + eta
    ctx.metrics.fracture = float(num / den)
