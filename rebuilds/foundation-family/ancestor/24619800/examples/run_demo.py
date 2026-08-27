from __future__ import annotations

import os, sys
from pathlib import Path
# Allow running from a fresh clone without installation
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / 'src'))

import numpy as np

from bloomcore.engine_context import EngineContext
from bloomcore.xp_backend import XPBackend
from bloomcore.run.loop import run_step


def print_hook(kind: str, payload: dict) -> None:
    # keep it simple: show receipt kind and dtau id when present
    dtau = payload.get("dtau_id")
    if dtau:
        print(f"{kind}: {dtau}  anchors={payload.get('anchors')[:3]}  payload_keys={list(payload.get('payload', {}).keys())}")
    else:
        print(f"{kind}: {payload}")


def main() -> None:
    xp = XPBackend()

    n = 8
    rng = np.random.default_rng(7)

    # PSD-ish W
    A = rng.normal(size=(n, n))
    W = A.T @ A

    S0 = rng.normal(size=(n,))
    ctx = EngineContext(
        xp_backend=xp,
        dt=1.0,
        state={
            "S": S0.copy(),
            "S_prev": S0.copy(),
        },
        params={
            "W": W,
            "fracture_eta": 1e-6,
            "identity_alpha": 0.9,
            "realign_alpha": 0.1,
            "realign_beta": 0.01,
            "fracture_grad_scale": 1.0,
            "dream_gamma": 0.05,
            "mirror_lambda": 0.05,
        },
        receipt_hook=print_hook,
    )

    # optional network example
    ctx.state["nodes"] = {
        "a": rng.normal(size=(n,)),
        "b": rng.normal(size=(n,)),
        "c": rng.normal(size=(n,)),
    }
    ctx.state["node_fracture"] = {"a": 0.1, "b": 0.2, "c": 0.05}

    for step in range(5):
        # toy "contradictions": random pairwise deltas
        contradictions = [
            {"x_i": rng.normal(size=(n,)), "x_j": rng.normal(size=(n,))},
            {"x_i": rng.normal(size=(n,)), "x_j": rng.normal(size=(n,))},
        ]
        run_step(ctx, contradiction_pairs=contradictions)

        print(
            f"t={ctx.t:.1f}  coherence={ctx.metrics.coherence:.4f}  "
            f"fracture={ctx.metrics.fracture:.4f}  identity_drift={ctx.metrics.identity_drift:.4f}  "
            f"netC={ctx.metrics.network_coherence}  netF={ctx.metrics.network_fracture}"
        )


if __name__ == "__main__":
    main()
