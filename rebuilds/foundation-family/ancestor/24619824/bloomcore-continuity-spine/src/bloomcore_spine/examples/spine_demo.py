"""
examples/spine_demo.py

Runs the BLOOMCORE pseudo-spectral engine + ContinuitySpine together (host-side),
and prints only emitted RECOUPLE_SIGNAL events.

OSS-safe: no gates, no ECA, no semantic mapping.

Prereq:
- bloomcore-engine must be importable (e.g. `pip install -e ../bloomcore-engine`)
- jax + jaxlib installed

Run:
  python -m bloomcore_spine.examples.spine_demo
"""
from __future__ import annotations

import time
import jax
import jax.numpy as jnp

from bloomcore_spine.continuity_spine import ContinuitySpine, SpineConfig


def _to_float(x):
    return float(jax.device_get(x))


def main():
    def printer(kind: str, payload: dict) -> None:
        if kind == "BLOOMCORE.RECOUPLE_SIGNAL.v1":
            print("\n=== RECOUPLE_SIGNAL ===")
            print("tick:", payload.get("tick"), "id:", payload.get("signal_id"))
            print("actions:", payload.get("actions"))
            r = payload.get("rationale", {})
            print("r.bandwidth:", r.get("recursion_bandwidth", {}))
            print("r.latency:", r.get("latency_asymmetry", {}))
            print("r.skew:", r.get("influence_skew", {}))
            print("r.flags:", r.get("flags", {}))

    cfg = SpineConfig(
        silent_after_sec=2.0,
        max_age_high_sec=1.0,
        min_receipts_per_sec=10.0,
        dominance_share_top1=0.80,
        emit_signals_every_events=8,
        emit_invariants_every_events=16,
        bandwidth_window_sec=1.5,
    )
    spine = ContinuitySpine(cfg=cfg, emit_hook=printer)

    from bloomcore_engine.bloomcore_coupling import (
        BloomState,
        StepConfig,
        PDEConfig,
        default_policy_chain_v12,
        run_steps_jax,
    )

    H, W = 64, 64
    key = jax.random.PRNGKey(0)
    u0 = jax.random.normal(key, (H, W)) * 0.05
    Xi0 = jnp.zeros((H, W), dtype=jnp.float32)

    st = BloomState(tick=jnp.int32(0), u=u0, Xi=Xi0, key=key)
    policy = default_policy_chain_v12()
    step_cfg = StepConfig(pde=PDEConfig())

    total_steps = 128
    chunk = 16
    remaining = total_steps

    spine.hook("BLOOMCORE.FIELD_PULSE.v1", {
        "tick": 0,
        "source_id": "engine",
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "u_mean": 0.0, "u_std": 0.0, "psi_mean": 0.0, "psi_std": 0.0, "Xi_mean": 0.0, "Xi_std": 0.0,
    })

    while remaining > 0:
        n = min(chunk, remaining)
        st, metrics = run_steps_jax(st, policy, step_cfg, steps=n)

        last = {k: v[-1] for k, v in metrics.items()}
        tick = int(jax.device_get(st.tick))

        spine.hook("BLOOMCORE.FIELD_PULSE.v1", {
            "tick": tick,
            "source_id": "engine",
            "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "u_mean": _to_float(last["u_mean"]),
            "u_std": _to_float(last["u_std"]),
            "psi_mean": _to_float(last["psi_mean"]),
            "psi_std": _to_float(last["psi_std"]),
            "Xi_mean": _to_float(last["Xi_mean"]),
            "Xi_std": _to_float(last["Xi_std"]),
        })

        if tick % 32 == 0:
            time.sleep(1.25)

        remaining -= n

    print("\nDone. Final tick:", int(jax.device_get(st.tick)))


if __name__ == "__main__":
    main()
