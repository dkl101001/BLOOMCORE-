from __future__ import annotations

from typing import Sequence

from ..engine_context import EngineContext


def apply_dreamloop(ctx: EngineContext, lags: Sequence[int], weights: Sequence[float]) -> None:
    """Dreamloop temporal smoothing (toy).

    D(t) = Σ_k w_k (S(t) - S(t-k))
    S <- S - γ D(t)

    Expects:
      ctx.state["S_hist"] : list of past S vectors (append each step)
      ctx.params["dream_gamma"] optional
    """
    if not lags:
        return

    S = ctx.state["S"]
    S_hist = ctx.state.setdefault("S_hist", [])
    S_hist.append(S.copy())

    max_lag = int(max(lags))
    if len(S_hist) <= max_lag:
        return

    gamma = float(ctx.params.get("dream_gamma", 0.05))
    D = ctx.xp_backend.zeros(S.shape)

    for k, w in zip(lags, weights):
        k = int(k)
        S_t = S_hist[-1]
        S_tk = S_hist[-1 - k]
        D = D + float(w) * (S_t - S_tk)

    ctx.state["S"] = S - gamma * D
