# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

"""
Smoke test for bloomcore-engine.
Runs a few steps on a small grid and prints metrics.
"""
import jax
import jax.numpy as jnp

from bloomcore_engine.bloomcore_coupling import (
    BloomState,
    StepConfig,
    PDEConfig,
    default_policy_chain_v12,
    run_steps_jax,
)

def main():
    H, W = 64, 64
    key = jax.random.PRNGKey(0)
    u0 = jax.random.normal(key, (H, W)) * 0.1
    Xi0 = jnp.zeros((H, W), dtype=jnp.float32)

    st0 = BloomState(tick=jnp.int32(0), u=u0, Xi=Xi0, key=key)
    policy = default_policy_chain_v12()
    cfg = StepConfig(pde=PDEConfig())

    stN, metrics = run_steps_jax(st0, policy, cfg, steps=32)

    # Pull last metrics
    last = {k: float(jax.device_get(v)[-1]) if hasattr(v, "shape") and v.shape else float(jax.device_get(v))
            for k, v in metrics.items()}
    print("ok", last)

if __name__ == "__main__":
    main()
