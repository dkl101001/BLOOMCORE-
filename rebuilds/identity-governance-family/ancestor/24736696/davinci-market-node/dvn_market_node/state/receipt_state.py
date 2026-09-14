from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .models import StateKey


def latest_state_step(path: Path, key: StateKey) -> Optional[Dict[str, Any]]:
    """Scan receipts JSONL for latest STATE.STEP.v1 matching state_key.

    ...
    """
    if not path.exists():
        return None
    target = key.to_str()
    last: Optional[Dict[str, Any]] = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("type") != "STATE.STEP.v1":
                continue
            if rec.get("state_key") != target:
                continue
            last = rec
    return last