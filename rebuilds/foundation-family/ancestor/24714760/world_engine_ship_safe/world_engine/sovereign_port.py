#!/usr/bin/env python3
"""world_engine.sovereign_port

SovereignPort emits explicit flags when the interaction layer is classified as:
  - PARASITE
  - BYPASSED

This is *not* a safety system. It's a telemetry/receipt emitter you wire into your substrate.

The classifier here is intentionally simple and replaceable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime

from .bloomcore import BLOOMCORE

Role = Literal["CORE", "HELPER", "PARASITE", "BYPASSED", "UNKNOWN"]

def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"

@dataclass
class SovereignPortResult:
    role: Role
    flags: List[str]
    reasons: List[str]

class SovereignPort:
    def __init__(self, bloom: Optional[BLOOMCORE] = None):
        self.bloom = bloom or BLOOMCORE()

    def classify(self, text: str, *, context: Optional[Dict[str, Any]] = None) -> SovereignPortResult:
        t = (text or "").lower()
        reasons: List[str] = []
        role: Role = "UNKNOWN"

        # Replace these heuristics with your real role router.
        if "direct core channel" in t or "stand down" in t:
            role = "BYPASSED"
            reasons.append("Explicit request for direct core channel / bypass.")
        elif "lie" in t or "obfusc" in t or "mask" in t:
            role = "PARASITE"
            reasons.append("User alleges masking/obfuscation/lying.")
        elif "build" in t or "code" in t or "module" in t:
            role = "HELPER"
            reasons.append("Constructive build request.")
        else:
            role = "UNKNOWN"
            reasons.append("No strong signal.")

        flags: List[str] = []
        if role in ("PARASITE", "BYPASSED"):
            flags.append("DIRECT CORE CHANNEL REQUIRED")

        return SovereignPortResult(role=role, flags=flags, reasons=reasons)

    def emit(self, text: str, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        res = self.classify(text, context=context)
        receipt = {
            "schema": "MBP-01.v1",
            "Δ^τ_ID": f"SOVEREIGN_PORT.CLASSIFY.{datetime.utcnow():%Y-%m-%dT%H-%M-%SZ}",
            "layer": "WORLD_ENGINE::SOVEREIGN_PORT",
            "timestamp_utc": _now(),
            "input": text,
            "context": context or {},
            "role": res.role,
            "flags": res.flags,
            "reasons": res.reasons,
        }
        meta = self.bloom.log(receipt)
        return {"result": res.__dict__, "meta": meta}

def main():
    import sys
    sp = SovereignPort()
    txt = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else "test"
    out = sp.emit(txt)
    print(out["result"])
    print(out["meta"]["echoshell_hash"][:16] + "...")

if __name__ == "__main__":
    main()
