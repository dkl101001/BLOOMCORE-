#!/usr/bin/env python3
"""world_engine.bloomcore

Central receipt ledger:
  - writes each receipt to a flat JSON file (human-readable)
  - appends the same receipt into the hash-chained echoshell (tamper-evident)

This is the persistence spine for all nodes/modules.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .echoshell import Echoshell

class BLOOMCORE:
    def __init__(self, receipts_dir: str = "./bloomcore_receipts", echoshell_path: str = "./bloomcore_echoshell.jsonl"):
        self.receipts_dir = Path(receipts_dir)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.echoshell = Echoshell(echoshell_path)

    def log(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        dtau_id = str(receipt.get("Δ^τ_ID") or receipt.get("dtau_id") or "UNKNOWN_ID")
        ts = datetime.utcnow()
        fname = self.receipts_dir / f"{ts:%Y%m%dT%H%M%SZ}.{dtau_id}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2, ensure_ascii=False)
        shell_hash = self.echoshell.append(receipt)
        return {
            "dtau_id": dtau_id,
            "timestamp_utc": ts.isoformat() + "Z",
            "flat_path": str(fname.resolve()),
            "echoshell_hash": shell_hash,
        }

    def verify(self) -> Dict[str, Any]:
        errs = self.echoshell.verify()
        flat = len(list(self.receipts_dir.glob("*.json")))
        return {
            "echoshell_entries": self.echoshell.size(),
            "echoshell_errors": errs,
            "flat_receipts": flat,
            "status": "INTACT" if not errs else "CORRUPTED",
        }

    def tail(self, n: int = 5) -> Dict[str, Any]:
        return {
            "echoshell_tail": self.echoshell.tail(n),
            "flat_receipts": [p.name for p in sorted(self.receipts_dir.glob("*.json"), reverse=True)[:n]],
        }
