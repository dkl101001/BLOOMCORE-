# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class ReceiptChain:
    """Deterministic witness chain; it does not govern the transition."""

    head: str = "0" * 64
    receipts: list[dict[str, Any]] = field(default_factory=list)

    def append(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        unsigned = {"kind": kind, "payload": payload, "prev_hash": self.head}
        digest = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
        receipt = {**unsigned, "hash": digest}
        self.receipts.append(receipt)
        self.head = digest
        return receipt

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
