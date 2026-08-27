# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, Any, Iterator, Optional, Tuple

@dataclass
class TailState:
    offset: int = 0
    head_hash: str = "0"*64

def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)

def append_jsonl(path: str, obj: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def iter_new_receipts(path: str, state: TailState) -> Iterator[Tuple[Dict[str, Any], int]]:
    if not os.path.exists(path):
        return
        yield  # pragma: no cover
    with open(path, "r", encoding="utf-8") as f:
        f.seek(state.offset)
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # partial line (writer mid-write) -> rewind and wait
                f.seek(pos)
                break
            state.offset = f.tell()
            yield obj, state.offset

def sleep_ms(ms: int) -> None:
    time.sleep(max(0, ms)/1000.0)

def load_state(path: str) -> TailState:
    if not path or not os.path.exists(path):
        return TailState()
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return TailState(offset=int(obj.get("offset", 0)), head_hash=str(obj.get("head_hash", "0"*64)))

def save_state(path: str, state: TailState) -> None:
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"offset": state.offset, "head_hash": state.head_hash}, f, indent=2, ensure_ascii=False)
