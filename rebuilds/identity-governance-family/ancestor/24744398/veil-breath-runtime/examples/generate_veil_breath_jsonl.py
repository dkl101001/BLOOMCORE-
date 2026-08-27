#!/usr/bin/env python3
from __future__ import annotations

import json
import random
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from veil_breath_runtime.receipt_chain import stamp_chain_hash  # noqa: E402
from veil_breath_runtime.veil_breath import VeilBreathCfg, VeilBreathState, veil_breath_step  # noqa: E402


def main() -> int:
    out = ROOT / "examples" / "sample_outputs" / "veil_breath_sample.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    cfg = VeilBreathCfg()
    st = VeilBreathState()
    last_hash = "GENESIS"

    with out.open("w", encoding="utf-8") as f:
        coherence = 0.65
        for t in range(60):
            rgb = {
                "r": min(1.0, max(0.0, random.random() * 0.6 + (0.25 if t > 25 else 0.0))),
                "g": min(1.0, max(0.0, random.random() * 0.6 + (0.20 if t > 25 else 0.0))),
                "b": min(1.0, max(0.0, random.random() * 0.6 + (0.30 if t > 25 else 0.0))),
            }
            vel = {
                "dv_dt": random.random() * (0.9 if t > 25 else 0.4),
                "step_rate": random.random() * (0.9 if t > 25 else 0.4),
                "proposal_entropy": random.random() * (0.9 if t > 25 else 0.4),
            }
            intent = "INTENT_HASH_DEMO" if t >= 20 else ""

            st, mixture, payload = veil_breath_step(st, rgb, vel, coherence, intent, cfg)

            receipt = {
                "Δ^τ_kind": "Δ^τ-VEIL_BREATH_STEP",
                **payload,
            }
            receipt = stamp_chain_hash(receipt, last_hash)
            last_hash = receipt["hash"]

            f.write(json.dumps(receipt, ensure_ascii=False) + "\n")

            coherence = max(0.2, min(0.9, coherence + (0.01 if mixture["recompose"] > 1.0 else -0.005)))

    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
