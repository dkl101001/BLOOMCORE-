from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class QuantizeSpec:
    """Quantization parameters used for deterministic receipt hashing."""
    scheme: str = "fixed_decimal"
    decimals: int = 8
    nan_sentinel: float = 0.0


def canonical_json_bytes(obj: Dict[str, Any]) -> bytes:
    """Canonical JSON bytes for hashing (sorted keys, stable separators)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def quantize_float(x: float, q: QuantizeSpec) -> float:
    """Quantize a float for deterministic hashing. NaN/inf -> sentinel."""
    if x != x:  # NaN
        return float(q.nan_sentinel)
    if x == float("inf") or x == float("-inf"):
        return float(q.nan_sentinel)
    if q.scheme == "fixed_decimal":
        # Round to fixed decimals; JSON will serialize deterministically with this value.
        return float(round(float(x), int(q.decimals)))
    raise ValueError(f"Unknown quantization scheme: {q.scheme!r}")


def quantize_payload(payload: Dict[str, Any], q: QuantizeSpec, *, float_keys: Optional[list[str]] = None) -> Dict[str, Any]:
    """Return a shallow-quantized copy for hashing."""
    out = dict(payload)
    if float_keys is None:
        # Quantize all top-level floats by default (except meta dicts).
        for k, v in list(out.items()):
            if isinstance(v, float):
                out[k] = quantize_float(v, q)
        return out

    for k in float_keys:
        if k in out and isinstance(out[k], (float, int)):
            out[k] = quantize_float(float(out[k]), q)
    return out


def hash_receipt(payload_for_hash: Dict[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes(payload_for_hash))
