# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def invalid_numbers(value: Any, path: str = "") -> dict[str, str]:
    """Retain non-finite classifications by path, never silently coerce to zero."""
    if isinstance(value, float) and not math.isfinite(value):
        return {path: "NaN" if math.isnan(value) else ("+Infinity" if value > 0 else "-Infinity")}
    result: dict[str, str] = {}
    items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, (list, tuple)) else ()
    for key, item in items:
        result.update(invalid_numbers(item, f"{path}/{key}"))
    return result


def finite_view(value: Any) -> Any:
    """v2 evidence projection: non-finite numbers become null; residue is separate."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: finite_view(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_view(item) for item in value]
    return value


@dataclass
class ReceiptChain:
    """Deterministic external witnesses; receipts do not govern decisions."""

    head: str = "0" * 64
    receipts: list[dict[str, Any]] = field(default_factory=list)

    def append(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        unsigned = {"kind": kind, "payload": payload, "prev_hash": self.head}
        digest = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
        # Snapshot before publishing: later caller mutations cannot corrupt custody.
        receipt = json.loads(canonical_json({**unsigned, "hash": digest}))
        self.receipts.append(receipt)
        self.head = digest
        return json.loads(canonical_json(receipt))

    def verify(self) -> bool:
        previous = "0" * 64
        for receipt in self.receipts:
            unsigned = {
                "kind": receipt["kind"],
                "payload": receipt["payload"],
                "prev_hash": previous,
            }
            expected = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
            if receipt.get("prev_hash") != previous or receipt.get("hash") != expected:
                return False
            previous = expected
        return previous == self.head
