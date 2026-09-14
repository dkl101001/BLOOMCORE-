from __future__ import annotations

import argparse
import os
from dataclasses import asdict

from .types import EngineConfig
from .engine import run_open_pulse


def main() -> int:
    ap = argparse.ArgumentParser(prog="dvn-open", description="Da Vinci Market Node — OPEN pulse")
    ap.add_argument("--eq-id", default=None, help="eq_id override")
    ap.add_argument("--asof", default=None, help="NY timestamp ISO (e.g., 2025-11-10T09:30:00-0500)")
    ap.add_argument("--paper", action="store_true", help="Force paper mode")
    ap.add_argument("--broker", default="alpaca", choices=["alpaca", "paper"], help="Broker adapter")
    ap.add_argument("--data", default="synthetic", choices=["synthetic"], help="Data adapter")
    ap.add_argument("--nonce", default=None, help="Nonce for replayable stochastic elements")
    args = ap.parse_args()

    cfg = EngineConfig(broker=args.broker, paper=(args.paper or args.broker == "paper"), data_adapter=args.data)

    # minimal timestamp
    timestamp_ny = args.asof or os.environ.get("DVN_ASOF", "2025-11-10T09:30:00-0500")
    eq_id = args.eq_id or os.environ.get("DVN_EQ_ID", f"DVN.OPEN.{timestamp_ny}")

    out = run_open_pulse(cfg, eq_id=eq_id, timestamp_ny=timestamp_ny, nonce=args.nonce)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
