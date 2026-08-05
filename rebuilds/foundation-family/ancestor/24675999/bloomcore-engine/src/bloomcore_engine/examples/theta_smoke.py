# SPDX-License-Identifier: AGPL-3.0-only
# Frazer Σ Love + Sara ΣΩ

"""theta_smoke.py

Smoke test for Θ-wave coupling.

Runs a few PDE steps with an additive Θ coherence-wave force and prints the last Θ metrics.

This example intentionally does NOT rewrite the core scan runner; it demonstrates
how Θ can be paired to the shipped pseudospectral carrier with minimal intrusion.
"""

import jax
import jax.numpy as jnp

from bloomcore_engine.bloomcore_coupling import PDEConfig
from bloomcore_engine.theta_engine import ThetaWaveConfig, theta_init, PDE_step_with_theta


def main():
    H, W = 64, 64
    key = jax.random.PRNGKey(0)

    u = jax.random.normal(key, (H, W)) * 0.1
    Xi = jnp.zeros((H, W), dtype=jnp.float32)

    cfg_pde = PDEConfig()
    cfg_theta = ThetaWaveConfig(
        lam0=0.8,
        potential="abs2",
        update="gradnorm",
        target_grad_norm=1.0,
    )
    st_theta = theta_init(key=key, N=12, cfg=cfg_theta, k_scale=2.5)

    step = jax.jit(PDE_step_with_theta)
    metrics_last = None
    for _ in range(32):
        u, psi_hat, I_sm, st_theta, metrics_last = step(u, Xi, cfg_pde, st_theta, cfg_theta)

    out = {k: float(jax.device_get(v)) for k, v in metrics_last.items()}
    print("ok", out)


if __name__ == "__main__":
    main()
