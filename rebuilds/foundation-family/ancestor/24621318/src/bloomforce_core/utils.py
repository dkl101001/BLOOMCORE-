from __future__ import annotations

from typing import Any
import time, json, hashlib


def now_ts() -> float:
    return time.time()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_obj(obj: Any) -> str:
    return sha256_hex(canonical_json(obj))


def clamp01(x: float) -> float:
    try:
        fx = float(x)
        return 0.0 if fx < 0.0 else 1.0 if fx > 1.0 else fx
    except Exception:
        return 0.0
