# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Optional, Tuple

from .types import Receipt

def _expand(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def parse_receipt_line(line: str) -> Optional[Receipt]:
    line = line.strip()
    if not line:
        return None
    obj = json.loads(line)
    return Receipt(
        r_id=str(obj["r_id"]),
        ts=_safe_float(obj.get("ts", 0.0)),
        kind=str(obj["kind"]),
        payload=dict(obj.get("payload") or {}),
        prev_hash=str(obj.get("prev_hash", "")),
        hash=str(obj.get("hash", "")),
    )

@dataclass
class TailState:
    offset: int = 0

def load_state(path: str) -> TailState:
    path = _expand(path)
    if not os.path.exists(path):
        return TailState(offset=0)
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return TailState(offset=int(obj.get("offset", 0)))

def save_state(path: str, state: TailState) -> None:
    path = _expand(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"offset": int(state.offset)}, f)
    os.replace(tmp, path)

def iter_new_receipts(ledger_path: str, *, state: TailState) -> Iterator[Tuple[Receipt, int]]:
    ledger_path = _expand(ledger_path)
    if not os.path.exists(ledger_path):
        return
    with open(ledger_path, "r", encoding="utf-8") as f:
        f.seek(state.offset)
        while True:
            line = f.readline()
            if not line:
                break
            r = parse_receipt_line(line)
            if r is None:
                continue
            yield r, f.tell()

def append_jsonl(ledger_path: str, obj: Dict[str, Any]) -> None:
    ledger_path = _expand(ledger_path)
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n")

def sleep_ms(ms: int) -> None:
    time.sleep(max(0.0, float(ms) / 1000.0))
