# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import argparse
import os
import json

from executor_lite.core.config import load_executor_config
from executor_lite.core.ledger_io import TailState, load_state, save_state, iter_new_receipts
from executor_lite.core.executor import build_runtime, run_loop

def _expand(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))

def cmd_run(args: argparse.Namespace) -> None:
    cfg = load_executor_config(args.backend_config)
    state_path = args.state or os.path.join(os.path.dirname(_expand(args.ledger)), ".executor.state.json")
    state = load_state(state_path)
    runtime = build_runtime(
        ledger_path=args.ledger,
        gates=cfg.evidence_gates,
        backend_name=cfg.backend.active_backend,
        backend_cfg=cfg.backend.backends,
        state=state,
    )
    try:
        run_loop(runtime, poll_ms=int(args.poll_ms), dry_run=bool(args.dry_run), limit=None)
    finally:
        save_state(state_path, runtime.state)

def cmd_status(args: argparse.Namespace) -> None:
    state = TailState(offset=0)
    last = []
    for r, _ in iter_new_receipts(args.ledger, state=state):
        last.append((r.kind, r.hash))
        if len(last) > 20:
            last.pop(0)
    print("Ledger:", _expand(args.ledger))
    print("Last receipts:")
    for k, h in last[-10:]:
        print(" -", k, h[:16])

def cmd_replay(args: argparse.Namespace) -> None:
    target = str(args.from_hash)
    state = TailState(offset=0)
    found = False
    count = 0
    for r, _ in iter_new_receipts(args.ledger, state=state):
        if not found and r.hash == target:
            found = True
            continue
        if found and str(r.kind).upper().startswith("EXEC_"):
            print(json.dumps({"kind": r.kind, "hash": r.hash, "payload": r.payload}, ensure_ascii=False))
            count += 1
            if args.limit and count >= int(args.limit):
                break
    if not found:
        raise SystemExit(f"from-hash not found: {target}")

def cmd_backends(args: argparse.Namespace) -> None:
    cfg = load_executor_config(args.backend_config)
    print("active_backend:", cfg.backend.active_backend)
    print("available_backends:", ", ".join(sorted(cfg.backend.backends.keys())))

def cmd_dry_run(args: argparse.Namespace) -> None:
    cfg = load_executor_config(args.backend_config)
    state = TailState(offset=0)
    runtime = build_runtime(
        ledger_path=args.ledger,
        gates=cfg.evidence_gates,
        backend_name=cfg.backend.active_backend,
        backend_cfg=cfg.backend.backends,
        state=state,
    )
    n = run_loop(runtime, poll_ms=0, dry_run=True, limit=int(args.limit))
    print("dry-run processed commands:", n)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="executorctl")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Tail kernel ledger and execute EXEC_* commands.")
    r.add_argument("--ledger", required=True, help="Path to kernel ledger JSONL file.")
    r.add_argument("--backend-config", required=True, help="Path to backend config JSON.")
    r.add_argument("--state", default=None, help="Path to state file for tail offset.")
    r.add_argument("--poll-ms", default=250, help="Polling interval when idle.")
    r.add_argument("--dry-run", action="store_true", help="Emit EXEC_DONE without executing.")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("status", help="Show last receipts in ledger.")
    s.add_argument("--ledger", required=True)
    s.set_defaults(func=cmd_status)

    rp = sub.add_parser("replay", help="Print EXEC_* receipts after a given receipt hash.")
    rp.add_argument("--ledger", required=True)
    rp.add_argument("--from-hash", required=True)
    rp.add_argument("--limit", default=50)
    rp.set_defaults(func=cmd_replay)

    b = sub.add_parser("backends", help="Show backend config summary.")
    b.add_argument("--backend-config", required=True)
    b.set_defaults(func=cmd_backends)

    d = sub.add_parser("dry-run", help="Process up to N commands in dry-run mode.")
    d.add_argument("--ledger", required=True)
    d.add_argument("--backend-config", required=True)
    d.add_argument("--limit", default=50)
    d.set_defaults(func=cmd_dry_run)

    return p

def main() -> None:
    p = build_parser()
    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
