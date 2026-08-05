# SPDX-License-Identifier: AGPL-3.0-or-later
import json
from pathlib import Path

from sentinel_lite_kernel.core.ledger_model import LedgerWriter
from sentinel_lite_kernel.core.ledger_io import append_jsonl, TailState, iter_new_receipts
from sentinel_lite_kernel.core.policy import AllowlistPolicy
from sentinel_lite_kernel.core.governor import build_runtime, process_once, KIND_PROPOSE

def test_basic_allowlist(tmp_path: Path):
    ledger = tmp_path/"ledger.jsonl"
    w = LedgerWriter()
    propose = w.make_receipt_obj(KIND_PROPOSE, {"command_id":"c1","scope":"local","action":"write_file","params":{"path":"x","content":"y"}})
    append_jsonl(str(ledger), propose)
    w.advance(propose)

    policy = AllowlistPolicy(policy_id="t", allow_scopes=["local"], allow_actions=["write_file"], deny_actions=[], require_evidence_for_actions=[])
    rt = build_runtime(str(ledger), policy=policy, head_hash=w.head_hash, offset=0)
    n = process_once(rt, emit_exec_cmd=True)
    assert n == 2
