# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import argparse
import os

from sentinel_lite_kernel.core.config import load_kernel_config
from sentinel_lite_kernel.core.ledger_io import load_state, save_state, sleep_ms
from sentinel_lite_kernel.core.governor import build_runtime, process_once, heartbeat

def _expand(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))

def cmd_step(args: argparse.Namespace) -> None:
    cfg = load_kernel_config(args.policy)
    st = load_state(args.state) if args.state else None
    offset = st.offset if st else 0
    head_hash = st.head_hash if st else "0"*64
    rt = build_runtime(args.ledger, policy=cfg.policy, head_hash=head_hash, offset=offset)
    n = process_once(rt, emit_exec_cmd=args.emit_exec_cmd)
    if args.heartbeat:
        heartbeat(rt, note="step")
    if args.state:
        save_state(args.state, rt.tail)
    print(n)

def cmd_run(args: argparse.Namespace) -> None:
    cfg = load_kernel_config(args.policy)
    state_path = args.state or os.path.join(os.path.dirname(_expand(args.ledger)), ".kernel.state.json")
    st = load_state(state_path)
    rt = build_runtime(args.ledger, policy=cfg.policy, head_hash=st.head_hash, offset=st.offset)
    if args.heartbeat:
        heartbeat(rt, note="start")
    while True:
        n = process_once(rt, emit_exec_cmd=args.emit_exec_cmd)
        save_state(state_path, rt.tail)
        if args.once:
            break
        sleep_ms(args.poll_ms if n == 0 else 0)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kernelctl")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("step", help="Process available proposals then exit.")
    s1.add_argument("--ledger", required=True)
    s1.add_argument("--policy", required=True)
    s1.add_argument("--state", default=None)
    s1.add_argument("--emit-exec-cmd", action="store_true")
    s1.add_argument("--heartbeat", action="store_true")
    s1.set_defaults(fn=cmd_step)

    s2 = sub.add_parser("run", help="Tail ledger and continuously process proposals.")
    s2.add_argument("--ledger", required=True)
    s2.add_argument("--policy", required=True)
    s2.add_argument("--state", default=None)
    s2.add_argument("--poll-ms", type=int, default=250)
    s2.add_argument("--emit-exec-cmd", action="store_true")
    s2.add_argument("--once", action="store_true", help="Run one loop iteration then exit.")
    s2.add_argument("--heartbeat", action="store_true")
    s2.set_defaults(fn=cmd_run)

    return p

def main() -> None:
    p = build_parser()
    args = p.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
