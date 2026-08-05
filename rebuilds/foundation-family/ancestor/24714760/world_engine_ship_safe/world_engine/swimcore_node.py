#!/usr/bin/env python3
"""world_engine.swimcore_node

Node 1 — SWIMCORE field monitor (minimal, standalone).

This module intentionally ships *only* a **telemetry sampler** with the
reserved channel names:
  - Co
  - Ii
  - GLR

Ship-safe contract (OSS):
  - These channels may be logged, tailed, graphed, and flagged.
  - This repo does **not** define their semantics, formulas, thresholds,
    regime selection, or any gating/authority behavior.
  - Any decision authority must live behind the public AuthorityAdapter
    boundary (private/provisional).

Replace the placeholder sampler with real SWIMCORE kernels later.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .bloomcore import BLOOMCORE


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class SwimcoreNodeConfig:
    interval_s: float = 2.0
    seed: Optional[int] = None


class SwimcoreNode:
    def __init__(self, cfg: Optional[SwimcoreNodeConfig] = None, bloom: Optional[BLOOMCORE] = None):
        self.cfg = cfg or SwimcoreNodeConfig()
        self.bloom = bloom or BLOOMCORE()
        self.rng = random.Random(self.cfg.seed)

    def sample_field(self) -> Dict[str, float]:
        """Placeholder dynamics: jitter within [0,1].

        NOTE: Values are deliberately *not* meaningful; they exist to exercise
        logging/audit paths and reserve the channel names.
        """
        Co = max(0.0, min(1.0, 0.55 + 0.25 * (self.rng.random() - 0.5)))
        Ii = max(0.0, min(1.0, 0.35 + 0.35 * (self.rng.random() - 0.5)))
        GLR = max(0.0, min(1.0, 0.65 + 0.20 * (self.rng.random() - 0.5)))
        return {"Co": Co, "Ii": Ii, "GLR": GLR}

    def emit_once(self) -> Dict[str, Any]:
        f = self.sample_field()
        receipt = {
            "schema": "MBP-01.v1",
            "Δ^τ_ID": f"SWIMCORE.FIELD.{datetime.utcnow():%Y-%m-%dT%H-%M-%SZ}",
            "layer": "WORLD_ENGINE::NODE_1::SWIMCORE",
            "timestamp_utc": _now_iso(),
            "field": f,
            "notes": "SWIMCORE telemetry channels (Co/Ii/GLR) — placeholder sampler; semantics live in SWIMCORE/authority, not OSS.",
        }
        return self.bloom.log(receipt)

    def run_forever(self) -> None:
        while True:
            meta = self.emit_once()
            print(f"[SWIMCORE] {meta['dtau_id']} {meta['echoshell_hash'][:12]}...")
            time.sleep(self.cfg.interval_s)


def main():
    node = SwimcoreNode()
    node.run_forever()


if __name__ == "__main__":
    main()
