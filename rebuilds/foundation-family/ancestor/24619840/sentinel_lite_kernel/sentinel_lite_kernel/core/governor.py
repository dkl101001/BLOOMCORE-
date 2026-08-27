# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

from .types import ProposedCommand
from .ledger_model import LedgerWriter
from .ledger_io import TailState, iter_new_receipts, append_jsonl
from .policy import Policy, SignalProvider

KIND_PROPOSE = "PROPOSE_CMD.v1"
KIND_DECISION = "DECISION.v1"
KIND_EXEC = "EXEC_CMD.v1"
KIND_HEARTBEAT = "KERNEL_HEARTBEAT.v1"

def _parse_proposal(obj: Dict[str, Any]) -> Optional[ProposedCommand]:
    if obj.get("kind") != KIND_PROPOSE:
        return None
    p = obj.get("payload", {})
    return ProposedCommand(
        command_id=str(p.get("command_id", "")),
        scope=str(p.get("scope", "")),
        action=str(p.get("action", "")),
        params=dict(p.get("params", {}) or {}),
        evidence_refs=list(p.get("evidence_refs") or []) or None,
        choice_hash=p.get("choice_hash"),
        audit_hash=p.get("audit_hash"),
    )

@dataclass
class KernelRuntime:
    ledger_path: str
    policy: Policy
    signal_provider: Optional[SignalProvider]
    writer: LedgerWriter
    tail: TailState

def build_runtime(ledger_path: str, policy: Policy, signal_provider: Optional[SignalProvider] = None, head_hash: str = "0"*64, offset: int = 0) -> KernelRuntime:
    return KernelRuntime(
        ledger_path=ledger_path,
        policy=policy,
        signal_provider=signal_provider,
        writer=LedgerWriter(head_hash=head_hash),
        tail=TailState(offset=offset, head_hash=head_hash),
    )

def process_once(rt: KernelRuntime, emit_exec_cmd: bool = False) -> int:
    wrote = 0
    for obj, _ in iter_new_receipts(rt.ledger_path, rt.tail):
        proposal = _parse_proposal(obj)
        if not proposal:
            rt.writer.advance(obj) if "hash" in obj else None
            rt.tail.head_hash = rt.writer.head_hash
            continue

        signals = rt.signal_provider.get_signals(proposal) if rt.signal_provider else None
        decision = rt.policy.decide(proposal, signals=signals)

        d_payload = {
            "command_id": proposal.command_id,
            "allowed": decision.allowed,
            "reasons": decision.reasons,
            "constraints": decision.constraints,
        }
        d_obj = rt.writer.make_receipt_obj(KIND_DECISION, d_payload, prev_hash=rt.writer.head_hash)
        append_jsonl(rt.ledger_path, d_obj)
        rt.writer.advance(d_obj)
        wrote += 1

        if decision.allowed and emit_exec_cmd:
            e_payload = {
                "command_id": proposal.command_id,
                "scope": proposal.scope,
                "action": proposal.action,
                "params": proposal.params,
                "constraints": decision.constraints,
                "evidence_refs": proposal.evidence_refs or [],
                "choice_hash": proposal.choice_hash,
                "audit_hash": proposal.audit_hash,
            }
            e_obj = rt.writer.make_receipt_obj(KIND_EXEC, e_payload, prev_hash=rt.writer.head_hash)
            append_jsonl(rt.ledger_path, e_obj)
            rt.writer.advance(e_obj)
            wrote += 1

        rt.tail.head_hash = rt.writer.head_hash

    return wrote

def heartbeat(rt: KernelRuntime, note: str = "") -> None:
    hb = rt.writer.make_receipt_obj(KIND_HEARTBEAT, {"note": note})
    append_jsonl(rt.ledger_path, hb)
    rt.writer.advance(hb)
    rt.tail.head_hash = rt.writer.head_hash
