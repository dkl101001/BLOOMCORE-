# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import json

import numpy as np

from .model import FireConfig, initial_oracle_state
from .orchestrator import run_oracle_cycle
from .receipts import ReceiptChain


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded foundation-family descendant")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--backend", choices=("oracle", "jax"), default="oracle")
    args = parser.parse_args()
    vector = np.asarray([0.25, -0.10, 0.40, 0.05], dtype=np.float32)
    field = np.linspace(-0.2, 0.2, 64, dtype=np.float32).reshape(8, 8)
    weight = np.eye(vector.size, dtype=np.float32)
    chain = ReceiptChain()
    last = None
    environment = {"backend": "ancestral-numpy-oracle"}
    if args.backend == "oracle":
        state = initial_oracle_state(vector=vector, field=field)
        for _ in range(args.steps):
            state, _, last = run_oracle_cycle(
                state,
                drive=np.zeros_like(vector),
                weight=weight,
                truth_flag=True,
                chain=chain,
                config=FireConfig(),
            )
    else:
        import jax
        import jax.numpy as jnp

        from .jax_backend import initial_jax_state
        from .orchestrator import run_jax_cycle

        state = initial_jax_state(vector=vector, field=field)
        environment = {
            "backend": "full-fire-jax",
            "jax": jax.__version__,
            "platform": jax.default_backend(),
            "devices": [str(device) for device in jax.devices()],
        }
        for _ in range(args.steps):
            state, _, last = run_jax_cycle(
                state,
                drive=jnp.zeros_like(state.vector),
                weight=jnp.asarray(weight),
                truth_flag=jnp.asarray(True),
                chain=chain,
                config=FireConfig(),
            )
    print(
        json.dumps(
            {
                "environment": environment,
                "steps": args.steps,
                "head": chain.head,
                "verified": chain.verify(),
                "last": last,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
