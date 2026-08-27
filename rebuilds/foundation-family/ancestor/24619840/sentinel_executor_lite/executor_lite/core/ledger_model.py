# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

@dataclass
class LedgerWriter:
    ledger_path: str

    def make_receipt_obj(self, kind: str, payload: Dict[str, Any], *, prev_hash: str, ts: Optional[float] = None) -> Dict[str, Any]:
        if ts is None:
            ts = time.time()
        core = {"ts": float(ts), "kind": str(kind), "payload": payload, "prev_hash": str(prev_hash)}
        h = _sha256_hex(_canonical_json(core))
        return {
            "r_id": f"{kind}:{h[:16]}",
            "ts": float(ts),
            "kind": str(kind),
            "payload": payload,
            "prev_hash": str(prev_hash),
            "hash": h,
        }
