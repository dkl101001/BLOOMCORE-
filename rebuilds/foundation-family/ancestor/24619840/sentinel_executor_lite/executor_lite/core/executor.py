# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from .types import Receipt
from .ledger_io import TailState, iter_new_receipts, append_jsonl, sleep_ms
from .ledger_model import LedgerWriter
from .evidence_gates import EvidenceGateSet, check_evidence
from .backend_loader import load_backend

COMMAND_PREFIX = "EXEC_"

def _now() -> float:
    return time.time()

def _command_id_from_receipt(r: Receipt) -> str:
    return r.hash

@dataclass
class ExecutorRuntime:
    ledger_path: str
    gates: EvidenceGateSet
    backend_name: str
    backend_cfg: Dict[str, Dict[str, Any]]
    state: TailState
    ledger_hashes_present: Set[str]
    ledger_kinds_present: Set[str]

def build_runtime(*, ledger_path: str, gates: EvidenceGateSet, backend_name: str, backend_cfg: Dict[str, Dict[str, Any]], state: TailState) -> ExecutorRuntime:
    return ExecutorRuntime(
        ledger_path=ledger_path,
        gates=gates,
        backend_name=backend_name,
        backend_cfg=backend_cfg,
        state=state,
        ledger_hashes_present=set(),
        ledger_kinds_present=set(),
    )

def _emit(runtime: ExecutorRuntime, kind: str, payload: Dict[str, Any], *, prev_hash: str) -> None:
    w = LedgerWriter(runtime.ledger_path)
    obj = w.make_receipt_obj(kind, payload, prev_hash=prev_hash)
    append_jsonl(runtime.ledger_path, obj)
    runtime.ledger_hashes_present.add(obj["hash"])
    runtime.ledger_kinds_present.add(obj["kind"])

def _seed_caches(runtime: ExecutorRuntime, *, max_lines: int = 20000) -> None:
    try:
        with open(runtime.ledger_path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            back = min(size, 4 * 1024 * 1024)
            f.seek(size - back)
            chunk = f.read().decode("utf-8", errors="ignore")
        lines = [ln for ln in chunk.splitlines() if ln.strip()]
        for ln in lines[-max_lines:]:
            try:
                obj = json.loads(ln)
                h = str(obj.get("hash", ""))
                k = str(obj.get("kind", ""))
                if h: runtime.ledger_hashes_present.add(h)
                if k: runtime.ledger_kinds_present.add(k)
            except Exception:
                continue
    except Exception:
        return

def run_loop(runtime: ExecutorRuntime, *, poll_ms: int = 250, dry_run: bool = False, limit: Optional[int] = None) -> int:
    backend = load_backend(runtime.backend_name, runtime.backend_cfg)
    processed = 0
    _seed_caches(runtime)

    while True:
        any_new = False
        for r, new_offset in iter_new_receipts(runtime.ledger_path, state=runtime.state):
            any_new = True
            runtime.state.offset = new_offset
            runtime.ledger_hashes_present.add(r.hash)
            runtime.ledger_kinds_present.add(r.kind)

            if not str(r.kind).upper().startswith(COMMAND_PREFIX):
                continue

            cmd_kind = str(r.kind).upper()
            cmd_payload = dict(r.payload or {})
            command_id = _command_id_from_receipt(r)

            evidence_refs = cmd_payload.get("evidence_refs") or cmd_payload.get("evidence") or []
            if isinstance(evidence_refs, str):
                evidence_refs = [evidence_refs]
            if not isinstance(evidence_refs, list):
                evidence_refs = []

            ok, gate_reason = check_evidence(
                gates=runtime.gates,
                cmd_kind=cmd_kind,
                evidence_refs=[str(x) for x in evidence_refs],
                ledger_hashes_present=runtime.ledger_hashes_present,
                ledger_kinds_present=runtime.ledger_kinds_present,
            )

            prev_hash = r.hash

            _emit(runtime, "EXEC_ACK", {
                "command_id": command_id,
                "cmd_kind": cmd_kind,
                "backend": backend.name,
                "ok_to_execute": bool(ok),
                "gate_reason": gate_reason,
                "ts": _now(),
            }, prev_hash=prev_hash)

            if not ok:
                _emit(runtime, "EXEC_FAIL", {
                    "command_id": command_id,
                    "cmd_kind": cmd_kind,
                    "backend": backend.name,
                    "reason": "EVIDENCE_GATE_DENIED",
                    "gate_reason": gate_reason,
                    "ts": _now(),
                }, prev_hash=prev_hash)
            else:
                if dry_run:
                    _emit(runtime, "EXEC_DONE", {
                        "command_id": command_id,
                        "cmd_kind": cmd_kind,
                        "backend": backend.name,
                        "dry_run": True,
                        "detail": {"note": "dry-run: no actuation performed"},
                        "ts": _now(),
                    }, prev_hash=prev_hash)
                else:
                    res = backend.execute(cmd_kind, cmd_payload)
                    if res.ok:
                        _emit(runtime, "EXEC_DONE", {
                            "command_id": command_id,
                            "cmd_kind": cmd_kind,
                            "backend": backend.name,
                            "detail": res.detail,
                            "ts": _now(),
                        }, prev_hash=prev_hash)
                    else:
                        _emit(runtime, "EXEC_FAIL", {
                            "command_id": command_id,
                            "cmd_kind": cmd_kind,
                            "backend": backend.name,
                            "reason": "BACKEND_EXEC_FAIL",
                            "detail": res.detail,
                            "ts": _now(),
                        }, prev_hash=prev_hash)

            processed += 1
            if limit is not None and processed >= int(limit):
                return processed

        if not any_new:
            sleep_ms(poll_ms)
