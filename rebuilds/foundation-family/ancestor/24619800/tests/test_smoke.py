from __future__ import annotations

import numpy as np

from bloomcore.engine_context import EngineContext
from bloomcore.xp_backend import XPBackend
from bloomcore.run.loop import run_step


def test_smoke_runs():
    xp = XPBackend()
    n = 4
    rng = np.random.default_rng(0)
    A = rng.normal(size=(n, n))
    W = A.T @ A
    S0 = rng.normal(size=(n,))

    receipts = []

    def hook(kind: str, payload: dict) -> None:
        receipts.append((kind, payload))

    ctx = EngineContext(
        xp_backend=xp,
        dt=1.0,
        state={"S": S0.copy(), "S_prev": S0.copy()},
        params={"W": W},
        receipt_hook=hook,
    )

    run_step(ctx, contradiction_pairs=[])
    assert len(ctx.history) == 1
    assert isinstance(ctx.metrics.coherence, float)
    assert isinstance(ctx.metrics.fracture, float)
    assert any(k.startswith("RECEIPT.DREAMLOOP") for k, _ in receipts)
