#!/usr/bin/env python3
"""world_engine.echoshell

Append-only, hash-linked JSONL log for Δ^τ receipts.

Each entry:
  - timestamp_utc
  - prev_hash
  - receipt (opaque dict)
  - hash = SHA-256(canonical_json(entry_without_hash))
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

class Echoshell:
    def __init__(self, log_path: str = "./bloomcore_echoshell.jsonl"):
        self.log_path = Path(log_path)
        self._tail_hash: Optional[str] = None
        self._load_tail()

    def _load_tail(self) -> None:
        if not self.log_path.exists():
            self._tail_hash = None
            return
        last = None
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = line
        if not last:
            self._tail_hash = None
            return
        try:
            entry = json.loads(last)
            self._tail_hash = entry.get("hash")
        except Exception:
            self._tail_hash = None

    def append(self, receipt: Dict[str, Any]) -> str:
        entry = {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "prev_hash": self._tail_hash,
            "receipt": receipt,
        }
        h = _sha256_hex(_canonical_json(entry))
        entry["hash"] = h
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self._tail_hash = h
        return h

    def size(self) -> int:
        if not self.log_path.exists():
            return 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())

    def tail(self, n: int = 10) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        out: List[Dict[str, Any]] = []
        for ln in reversed(lines[-n:]):
            try:
                out.append(json.loads(ln))
            except Exception:
                out.append({"corrupt_line": ln})
        return out

    def verify(self) -> List[str]:
        if not self.log_path.exists():
            return ["Echoshell file does not exist."]
        errors: List[str] = []
        prev_hash = None
        with open(self.log_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception as e:
                    errors.append(f"Line {i}: invalid JSON: {e}")
                    continue

                if prev_hash is not None and entry.get("prev_hash") != prev_hash:
                    errors.append(f"Line {i}: prev_hash mismatch (expected {prev_hash}, got {entry.get('prev_hash')})")

                stored = entry.get("hash")
                core = {k: v for k, v in entry.items() if k != "hash"}
                computed = _sha256_hex(_canonical_json(core))
                if stored != computed:
                    errors.append(f"Line {i}: hash mismatch (stored {stored}, computed {computed})")

                prev_hash = stored
        return errors
