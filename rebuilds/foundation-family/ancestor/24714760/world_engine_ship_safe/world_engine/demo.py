#!/usr/bin/env python3
"""world_engine.demo

A tiny "one-shot" run that:
- starts Node0 bloomcore
- emits a NOTE
- runs SovereignPort
- runs Mirrorseed cycle once
- emits one Swimcore sample

Run:
    python -m world_engine.demo
"""

from __future__ import annotations

from .bloomcore import BLOOMCORE
from .sovereign_port import SovereignPort
from .mirrorseed_cycle import MirrorseedCycle
from .swimcore_node import SwimcoreNode, SwimcoreNodeConfig

def main():
    bloom = BLOOMCORE()
    bloom.log({"schema":"MBP-01.v1","Δ^τ_ID":"DEMO.NOTE","layer":"WORLD_ENGINE::DEMO","timestamp_utc":"NOW","text":"hello world engine"})
    sp = SovereignPort(bloom)
    sp.emit("build the module please", context={"demo": True})
    cyc = MirrorseedCycle()
    cyc.record_fracture("What contradiction are we ignoring?", source="DEMO", route="recursion_event")
    cyc.run_cycle_once(bloom=bloom)
    node = SwimcoreNode(cfg=SwimcoreNodeConfig(interval_s=0.1, seed=1), bloom=bloom)
    node.emit_once()
    print("demo complete; check bloomcore_receipts/ and bloomcore_echoshell.jsonl")

if __name__ == "__main__":
    main()
