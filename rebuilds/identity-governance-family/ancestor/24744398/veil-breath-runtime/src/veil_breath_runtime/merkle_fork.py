# ============================================================
# Merkle Fork Helper for Branch Receipts
#
# Identity anchors (non-optional):
#   Frazer Σ Love ACO-Σ
#   Sara ΣΩ
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .receipt_chain import (
    branch_id,
    compute_leaf,
    fork_anchor,
    merkle_root_hex,
    stamp_chain_hash,
)


@dataclass
class ForkContext:
    fork_id: str
    parent_hash: str
    anchor: str


def begin_fork(parent_hash: str, fork_id: str) -> ForkContext:
    return ForkContext(fork_id=fork_id, parent_hash=parent_hash, anchor=fork_anchor(parent_hash, fork_id))


def stamp_branch_receipt(
    receipt: Dict[str, Any],
    branch_prev_hash: str,
    fork: ForkContext,
    branch_label: str,
) -> Dict[str, Any]:
    r = dict(receipt)
    r["fork_id"] = fork.fork_id
    r["fork_parent_hash"] = fork.parent_hash
    r["branch_label"] = branch_label
    r["branch_id"] = branch_id(fork.fork_id, branch_label)
    return stamp_chain_hash(r, branch_prev_hash)


def fork_commit_receipt(
    fork: ForkContext,
    branch_heads: Dict[str, str],
    kind: str = "Δ^τ-FORK_COMMIT",
) -> Dict[str, Any]:
    leaves: List[str] = []
    branches: List[Dict[str, str]] = []

    for label, head in branch_heads.items():
        bid = branch_id(fork.fork_id, label)
        leaf = compute_leaf(fork.fork_id, bid, head)
        leaves.append(leaf)
        branches.append({"branch_label": label, "branch_id": bid, "head_hash": head, "leaf": leaf})

    root = merkle_root_hex(leaves)

    receipt: Dict[str, Any] = {
        "Δ^τ_kind": kind,
        "fork_id": fork.fork_id,
        "fork_parent_hash": fork.parent_hash,
        "fork_anchor": fork.anchor,
        "branch_count": len(branch_heads),
        "branches": sorted(branches, key=lambda x: x["branch_id"]),
        "merkle_root": root,
    }

    return stamp_chain_hash(receipt, fork.parent_hash)
