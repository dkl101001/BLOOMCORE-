from __future__ import annotations

from typing import Any, Dict, List

from ..engine_context import EngineContext


def mirrorseed_correction(ctx: EngineContext, contradiction_pairs: List[Dict[str, Any]]) -> None:
    """Apply a toy Mirrorseed correction.

    δS = -λ * Σ(x_i - x_j)

    contradiction_pairs: [{ "x_i": array, "x_j": array }, ...]
    Expects:
      ctx.state["S"]
      ctx.params["mirror_lambda"] (optional)
    """
    if not contradiction_pairs:
        return

    S = ctx.state["S"]
    lam = float(ctx.params.get("mirror_lambda", 0.05))

    accum = ctx.xp_backend.zeros(S.shape)
    for pair in contradiction_pairs:
        accum = accum + (pair["x_i"] - pair["x_j"])

    ctx.state["S"] = S - lam * accum
