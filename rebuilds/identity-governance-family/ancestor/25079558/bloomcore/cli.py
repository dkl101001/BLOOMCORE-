# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
import argparse
from typing import Optional
import sys

from .config import BLOOMCOREConfig
from .engine import run
from .receipts.writer import ReceiptWriter, chain_append
from .receipts.schema import Receipt

def cmd_run_sim(args: argparse.Namespace) -> int:
    cfg = BLOOMCOREConfig()
    summary, receipts = run(cfg, steps=args.steps, n_modes=args.modes, seed=args.seed)


    out_path = args.out
    header = Receipt(
        schema=cfg.schema,
        Δ_τ_ID="RECEIPT.RUN.START.v1",
        event="Run start (Sophia + Compassion)",
        operator="Frazer Σ Love + Sara ΣΩ",
        system_root="BLOOMCORE",
        law=cfg.law_compassion,
        tags=list(cfg.regime_tags) + ["run"],
        step=0,
        payload={"config": cfg.to_receipt_payload(), "steps": args.steps, "n_modes": args.modes, "seed": args.seed, "backend": summary.backend},
    )

    tail = Receipt(
        schema=cfg.schema,
        Δ_τ_ID="RECEIPT.RUN.END.v1",
        event="Run end (Sophia + Compassion)",
        operator="Frazer Σ Love + Sara ΣΩ",
        system_root="BLOOMCORE",
        law=cfg.law_compassion,
        tags=list(cfg.regime_tags) + ["run"],
        step=args.steps,
        payload={
            "backend": summary.backend,
            "final": {"psi": summary.final_psi, "C": summary.final_C, "zeta": summary.final_zeta},
            "median_Hdot": summary.median_Hdot,
            "sophia_accept_rate": summary.sophia_accept_rate,
        },
    )

    if args.append:
        # Atomic append per receipt atom; preserves chain across runs.
        chain_append(out_path, header, operator="Frazer Σ Love + Sara ΣΩ")
        for r in receipts:
            chain_append(out_path, r, operator="Frazer Σ Love + Sara ΣΩ")
        chain_append(out_path, tail, operator="Frazer Σ Love + Sara ΣΩ")
    else:
        # Overwrite: new ledger starting at genesis chain hash.
        with open(out_path, "w", encoding="utf-8") as fp:
            w = ReceiptWriter(fp, operator="Frazer Σ Love + Sara ΣΩ")
            w.write(header)
            for r in receipts:
                w.write(r)
            w.write(tail)

    print(f"backend={summary.backend} steps={summary.steps} modes={summary.n_modes} final_psi={summary.final_psi:.6f} final_C={summary.final_C:.6f} final_zeta={summary.final_zeta:.6f}")
    print(f"median_Hdot={summary.median_Hdot:.6e} sophia_accept_rate={summary.sophia_accept_rate:.3f}")
    print(f"receipts_written={out_path}")
    return 0

def main(argv: Optional[list[str]] = None) -> None:
    p = argparse.ArgumentParser(prog="bloomcore-sophia")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("run-sim", help="Run ΩGod·ΦField recursion with Compassion v5.2 + Sophia gate receipts.")
    ps.add_argument("--steps", type=int, default=256)
    ps.add_argument("--modes", type=int, default=128)
    ps.add_argument("--seed", type=int, default=0)
    ps.add_argument("--out", type=str, default="receipts.jsonl")
    ps.add_argument("--append", action="store_true", help="Append to existing JSONL ledger (hash-chained) instead of overwriting.")
    ps.set_defaults(func=cmd_run_sim)

    args = p.parse_args(argv)
    rc = args.func(args)
    raise SystemExit(rc)

if __name__ == "__main__":
    main()