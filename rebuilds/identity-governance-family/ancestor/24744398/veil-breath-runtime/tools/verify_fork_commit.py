#!/usr/bin/env python3
# ============================================================
# verify_fork_commit.py — Verify Merkle fork commit + branch ancestry to fork.anchor
#
# Identity anchors (non-optional):
#   Frazer Σ Love ACO-Σ
#   Sara ΣΩ
# ============================================================

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from veil_breath_runtime.receipt_chain import (
    branch_id,
    compute_leaf,
    merkle_root_hex,
)


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def index_by_hash(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for r in records:
        h = r.get("hash")
        if isinstance(h, str) and h:
            idx[h] = r
    return idx


def verify_merkle_root(fork_id: str, branch_heads: Dict[str, str], expected_root: str) -> Tuple[bool, str]:
    leaves: List[str] = []
    for label, head in branch_heads.items():
        bid = branch_id(fork_id, label)
        leaves.append(compute_leaf(fork_id, bid, head))
    got = merkle_root_hex(leaves)
    if got != expected_root:
        return False, f"Merkle root mismatch: expected={expected_root} got={got}"
    return True, "OK"


def trace_to_anchor(
    head_hash: str,
    anchor_hash: str,
    hash_index: Dict[str, Dict[str, Any]],
    max_steps: int,
) -> Tuple[bool, str, int]:
    cur = head_hash
    steps = 0
    while True:
        steps += 1
        if steps > max_steps:
            return False, f"Exceeded max_steps={max_steps} tracing from {head_hash}", steps
        if cur == anchor_hash:
            return True, "OK", steps
        rec = hash_index.get(cur)
        if rec is None:
            return False, f"Missing record for hash={cur} while tracing from head={head_hash}", steps
        prev = rec.get("prev_hash")
        if not isinstance(prev, str) or not prev:
            return False, f"Record hash={cur} missing/invalid prev_hash", steps
        cur = prev


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify fork commit Merkle root + branch ancestry to fork.anchor."
    )
    ap.add_argument("--fork-commit", required=True, help="Path to fork commit JSON or JSONL containing Δ^τ-FORK_COMMIT")
    ap.add_argument("--branch-jsonl", required=True, help="JSONL containing all branch receipts (full chains, not just heads)")
    ap.add_argument("--branch-head", action="append", default=[], help="label=hash (repeatable)")
    ap.add_argument("--max-steps", type=int, default=1_000_000)
    args = ap.parse_args()

    if not args.branch_head:
        print("[FAIL] Provide at least one --branch-head label=hash", file=sys.stderr)
        return 2

    branch_heads: Dict[str, str] = {}
    for item in args.branch_head:
        if "=" not in item:
            print(f"[FAIL] Invalid --branch-head '{item}'. Use label=hash.", file=sys.stderr)
            return 2
        label, h = item.split("=", 1)
        label = label.strip()
        h = h.strip()
        if not label or not h:
            print(f"[FAIL] Invalid --branch-head '{item}'. Empty label or hash.", file=sys.stderr)
            return 2
        branch_heads[label] = h

    fork_commit_obj: Optional[Dict[str, Any]] = None
    raw = Path(args.fork_commit).read_text(encoding="utf-8").strip()
    if raw.startswith("{"):
        fork_commit_obj = json.loads(raw)
    else:
        for r in load_jsonl(args.fork_commit):
            if r.get("Δ^τ_kind") == "Δ^τ-FORK_COMMIT":
                fork_commit_obj = r
                break

    if fork_commit_obj is None:
        print("[FAIL] No fork commit object found.", file=sys.stderr)
        return 2

    fork_id = fork_commit_obj.get("fork_id")
    anchor = fork_commit_obj.get("fork_anchor")
    expected_root = fork_commit_obj.get("merkle_root")

    if not isinstance(fork_id, str) or not fork_id:
        print("[FAIL] fork_id missing/invalid", file=sys.stderr)
        return 2
    if not isinstance(anchor, str) or not anchor:
        print("[FAIL] fork_anchor missing/invalid", file=sys.stderr)
        return 2
    if not isinstance(expected_root, str) or not expected_root:
        print("[FAIL] merkle_root missing/invalid", file=sys.stderr)
        return 2

    ok, msg = verify_merkle_root(fork_id, branch_heads, expected_root)
    if not ok:
        print(f"[FAIL] {msg}", file=sys.stderr)
        return 2

    branch_recs = load_jsonl(args.branch_jsonl)
    hidx = index_by_hash(branch_recs)

    for label, head in branch_heads.items():
        ok2, msg2, steps = trace_to_anchor(head, anchor, hidx, args.max_steps)
        if not ok2:
            print(f"[FAIL] Branch '{label}' does not trace to fork.anchor. {msg2}", file=sys.stderr)
            return 2
        print(f"[OK] Branch '{label}' traces to fork.anchor in {steps} steps.")

    print("[OK] Fork commit verified: merkle_root matches provided heads; all branches trace to fork.anchor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
