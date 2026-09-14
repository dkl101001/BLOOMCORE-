# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
import json
import hashlib
from typing import Any, Dict, Tuple

from .tags import normalize_tags

def _normalize(obj: Any) -> Any:
    # Ensure stable JSON across python versions: sort keys, convert tuples to lists, floats to repr with full precision.
    if isinstance(obj, dict):
        out = {}
        for k in sorted(obj.keys()):
            v = obj[k]
            if k == "tags":
                try:
                    out[k] = normalize_tags(v)  # type: ignore[arg-type]
                except Exception:
                    out[k] = _normalize(v)
            else:
                out[k] = _normalize(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]
    if isinstance(obj, float):
        # Use repr for full precision deterministic string -> parseable JSON number
        return float(repr(obj))
    return obj

def canonical_json_bytes(payload: Dict[str, Any]) -> bytes:
    norm = _normalize(payload)
    s = json.dumps(norm, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return s.encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def hash_receipt(payload: Dict[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes(payload))

def hash_chain(prev_hash: str, payload_hash: str) -> str:
    return sha256_hex((prev_hash + payload_hash).encode("utf-8"))
