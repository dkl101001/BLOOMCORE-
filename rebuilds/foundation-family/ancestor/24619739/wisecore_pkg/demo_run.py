# ============================================================
# LAW.WISECORE.v1 — demo_run.py
# ============================================================
# Title: WISECORE — Tiny Demo Runner (JAX Gate + MBP Receipts)
# Authors: Frazer Σ Love ACO-Σ ; Sara ΣΩ
# Status: ACTIVE
# ============================================================

from __future__ import annotations

import json

import jax.numpy as jnp

from wisecore_contract import wisecore_run_with_receipts, WiseCoreRunConfig
from wisecore_jax import WiseCoreThresh


def main() -> None:
    # --- Dummy inputs (replace with SWIM/ECA outputs) ---
    # phase_modes: could be complex wave components; here a tiny synthetic vector
    phase_modes = jnp.asarray([1.0 + 0.2j, 0.7 + 0.1j, 0.2 + 0.05j], dtype=jnp.complex64)

    # Hdot_series: energetic derivative samples; negative median => WuWei descent
    Hdot_series = jnp.asarray([-0.2, -0.1, -0.05, -0.12, -0.08], dtype=jnp.float32)

    friend_coherence = 0.45
    truth_flag = True

    relation_scope_id = "scope:friend"
    logos_form_id = "compact"

    cfg = WiseCoreRunConfig(
        thresh=WiseCoreThresh(phi_min_N_phase=0.2, friend_min_F=0.30, require_wuwei_descent=True)
    )

    receipts = wisecore_run_with_receipts(
        phase_modes=phase_modes,
        Hdot_series=Hdot_series,
        friend_coherence=friend_coherence,
        truth_flag=truth_flag,
        relation_scope_id=relation_scope_id,
        logos_form_id=logos_form_id,
        cfg=cfg,
    )

    print(json.dumps(receipts, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
