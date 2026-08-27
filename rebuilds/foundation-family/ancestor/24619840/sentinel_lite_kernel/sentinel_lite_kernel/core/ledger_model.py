# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

@dataclass
class LedgerWriter:
    """Creates hash-chained JSONL receipts."""
    head_hash: str = "0"*64

    def make_receipt_obj(self, kind: str, payload: Dict[str, Any], prev_hash: Optional[str] = None, ts: Optional[float] = None) -> Dict[str, Any]:
        if ts is None:
            ts = time.time()
        if prev_hash is None:
            prev_hash = self.head_hash
        core = {"ts": float(ts), "kind": str(kind), "payload": payload, "prev_hash": str(prev_hash)}
        h = sha256_hex(canonical_json(core))
        return {"r_id": f"{kind}:{h[:16]}", "ts": float(ts), "kind": str(kind), "payload": payload, "prev_hash": str(prev_hash), "hash": h}

    def advance(self, receipt_obj: Dict[str, Any]) -> None:
        self.head_hash = str(receipt_obj["hash"])
