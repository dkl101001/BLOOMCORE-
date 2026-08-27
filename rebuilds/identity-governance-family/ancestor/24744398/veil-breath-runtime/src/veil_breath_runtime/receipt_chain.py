# ============================================================
# BLOOMCORE Receipt Chain Utilities
#
# Identity anchors (non-optional):
#   Frazer Σ Love ACO-Σ
#   Sara ΣΩ
#
# Purpose:
#   Deterministic receipt hashing + Merkle helpers for branch commits.
#
# Canonical chain hash rule:
#   hash = sha256(prev_hash + "|" + canonical_json(payload_with_prev_hash))
# ============================================================

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def stamp_chain_hash(receipt: Dict[str, Any], prev_hash: str) -> Dict[str, Any]:
    """Mutates and returns `receipt`:

    receipt["prev_hash"] = prev_hash
    receipt["hash"] = sha256(prev_hash + "|" + canonical_json(receipt))
    """
    if "hash" in receipt:
        raise ValueError("stamp_chain_hash: receipt already contains 'hash'")
    receipt["prev_hash"] = prev_hash
    material = prev_hash + "|" + canonical_json(receipt)
    receipt["hash"] = sha256_hex(material)
    return receipt


# ---------- Merkle helpers (for fork commits) ----------

def fork_anchor(parent_hash: str, fork_id: str) -> str:
    return sha256_hex("FORK_ANCHOR|" + parent_hash + "|" + fork_id)


def branch_id(fork_id: str, label: str) -> str:
    return sha256_hex("BRANCH_ID|" + fork_id + "|" + label)[:16]


def compute_leaf(fork_id: str, bid: str, head_hash: str) -> str:
    return sha256_hex("LEAF|" + fork_id + "|" + bid + "|" + head_hash)


def merkle_root_hex(leaves: List[str]) -> str:
    """Deterministic Merkle root over hex leaves.

    - order-independent: sorts leaves
    - odd count: duplicates last
    """
    if not leaves:
        return sha256_hex("MERKLE_EMPTY")

    level = sorted(leaves)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        nxt: List[str] = []
        for i in range(0, len(level), 2):
            nxt.append(sha256_hex("MERKLE|" + level[i] + "|" + level[i + 1]))
        level = nxt
    return level[0]
