from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def event_id(payload: Dict[str, Any]) -> str:
    """Receipt/event id = sha256(canonical_json)."""
    return sha256_hex(canonical_dumps(payload))
