#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from veil_breath_runtime.merkle_fork import begin_fork, stamp_branch_receipt, fork_commit_receipt  # noqa: E402


def main() -> int:
    out_branch = ROOT / "examples" / "sample_outputs" / "fork_branches.jsonl"
    out_commit = ROOT / "examples" / "sample_outputs" / "fork_commit.json"
    out_branch.parent.mkdir(parents=True, exist_ok=True)

    parent_head = "PARENT_HEAD_DEMO_HASH"
    fork = begin_fork(parent_head, fork_id="VEIL_BREATH_FORK_DEMO")

    branch_heads = {
        "A.recompose_heavy": fork.anchor,
        "B.tails_heavy": fork.anchor,
        "C.accel_damped": fork.anchor,
    }

    # Write some receipts in each branch
    with out_branch.open("w", encoding="utf-8") as f:
        for i in range(5):
            for label in list(branch_heads.keys()):
                r = {
                    "Δ^τ_kind": "Δ^τ-BRANCH_STEP",
                    "i": i,
                    "note": f"demo step {i} in {label}",
                }
                r = stamp_branch_receipt(r, branch_heads[label], fork, label)
                branch_heads[label] = r["hash"]
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    commit = fork_commit_receipt(fork, branch_heads)
    out_commit.write_text(json.dumps(commit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote: {out_branch}")
    print(f"Wrote: {out_commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
