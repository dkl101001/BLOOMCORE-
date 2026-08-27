from __future__ import annotations

import argparse, json
from typing import Any, Dict, Optional

from .engine import Engine
from .types import ObsBundle
from .index import LedgerIndex
from .io import save_ledger_jsonl, load_ledger_jsonl


def _parse_obs_json(s: str) -> Dict[str, Any]:
    obj = json.loads(s)
    if not isinstance(obj, dict):
        raise ValueError("obs json must be an object/dict")
    return obj


def cmd_run(args: argparse.Namespace) -> int:
    eng = Engine()
    idx = LedgerIndex()

    base_obs: Optional[ObsBundle] = None
    if args.obs_json:
        d = _parse_obs_json(args.obs_json)
        base_obs = ObsBundle(
            psi_rho=float(d.get("psi_rho", 0.0)),
            grad_rho=float(d.get("grad_rho", 0.0)),
            delta_tau_mass=float(d.get("delta_tau_mass", 0.0)),
        )

    for i in range(int(args.steps)):
        obs = base_obs if base_obs is not None else ObsBundle(
            psi_rho=0.5,
            grad_rho=0.10 + 0.01 * i,
            delta_tau_mass=0.05,
        )
        state, r = eng.step(
            obs=obs,
            seed=(args.seed0 + i) if args.seed0 is not None else None,
            meta={"cli": True, "i": i},
        )
        idx.ingest(r)
        if args.print_receipts:
            print(
                f"[{i}] {r.kind} {r.r_id} tick={state.tick} x={state.x:.6f} force={state.last_force:.6f}"
            )

    ok = eng.ledger.verify_chain()
    print(f"ledger_ok={ok} receipts={len(eng.ledger.receipts)}")

    if args.summary:
        idx2 = LedgerIndex()
        for rr in eng.ledger.receipts:
            idx2.ingest(rr)
        print(json.dumps(idx2.summary(), indent=2, sort_keys=True))

    if args.save:
        save_ledger_jsonl(eng.ledger, args.save, overwrite=(not args.no_overwrite))
        print(f"saved_ledger={args.save}")

    return 0 if ok else 2


def cmd_verify(args: argparse.Namespace) -> int:
    led = load_ledger_jsonl(args.load, strict=True)
    print(f"loaded_ledger={args.load} receipts={len(led.receipts)} ledger_ok=True")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="python -m bloomforce_core", add_help=True)
    sub = p.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run", help="Run a small engine loop and emit receipts")
    runp.add_argument("--steps", type=int, default=10)
    runp.add_argument("--seed0", type=int, default=1337)
    runp.add_argument("--print-receipts", action="store_true")
    runp.add_argument("--summary", action="store_true")
    runp.add_argument("--obs-json", type=str, default="")
    runp.add_argument("--save", type=str, default="")
    runp.add_argument("--no-overwrite", action="store_true")
    runp.set_defaults(func=cmd_run)

    verp = sub.add_parser("verify", help="Verify a saved ledger JSONL file")
    verp.add_argument("--load", type=str, required=True)
    verp.set_defaults(func=cmd_verify)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
