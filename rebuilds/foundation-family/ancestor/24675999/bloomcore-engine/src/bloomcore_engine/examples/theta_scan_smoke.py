# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

"""theta_scan_smoke.py

Smoke test for the Θ-augmented scan runner.

Runs run_steps_jax_with_theta(...) for a short horizon and prints the final metrics.

This is OSS-safe and pairs cleanly with the shipped pseudo-spectral carrier.
"""

import jax
import jax.numpy as jnp

from bloomcore_engine.bloomcore_coupling import StepConfig, PDEConfig, default_policy_chain_v12
from bloomcore_engine.theta_engine import (
    BloomThetaState,
    ThetaWaveConfig,
    theta_init,
    run_steps_jax_with_theta,
)


def main():
    H, W = 64, 64
    key = jax.random.PRNGKey(0)
    k1, k2 = jax.random.split(key)

    u0 = jax.random.normal(k1, (H, W)) * 0.1
    Xi0 = jnp.zeros((H, W), dtype=jnp.float32)

    cfg = StepConfig(pde=PDEConfig())
    policy = default_policy_chain_v12()

    cfg_theta = ThetaWaveConfig(
        lam0=0.8,
        potential="abs2",
        update="gradnorm",
        target_grad_norm=1.0,
    )
    st_theta0 = theta_init(key=k2, N=12, cfg=cfg_theta, k_scale=2.5)

    st0 = BloomThetaState(tick=jnp.int32(0), u=u0, Xi=Xi0, theta=st_theta0, key=key)

    # JIT the scan runner
    runner = jax.jit(run_steps_jax_with_theta, static_argnames=("steps",))
    stN, metrics = runner(st0, policy, cfg, cfg_theta, steps=64)

    # Print the last metric row
    last = {k: float(jax.device_get(v[-1])) for k, v in metrics.items()}
    print("ok", last)


if __name__ == "__main__":
    main()
