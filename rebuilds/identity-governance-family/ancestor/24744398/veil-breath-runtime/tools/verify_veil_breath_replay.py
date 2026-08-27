#!/usr/bin/env python3
# ============================================================
# verify_veil_breath_replay.py — Minimal deterministic replay verifier
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
from typing import Any, Dict

# Make src importable when running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from veil_breath_runtime.receipt_chain import canonical_json, sha256_hex  # noqa: E402
from veil_breath_runtime.veil_breath import VeilBreathCfg, VeilBreathState, veil_breath_step  # noqa: E402


def compute_chain_hash(prev_hash: str, payload_no_hash: Dict[str, Any]) -> str:
    material = prev_hash + "|" + canonical_json(payload_no_hash)
    return sha256_hex(material)


def float_close(a: float, b: float, tol: float) -> bool:
    return abs(float(a) - float(b)) <= tol


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl_path")
    ap.add_argument("--verify-hash-chain", action="store_true")
    ap.add_argument("--tol", type=float, default=1e-9)
    args = ap.parse_args()

    cfg = VeilBreathCfg()
    st = VeilBreathState()
    prev_hash = "GENESIS"

    with open(args.jsonl_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)

            rgb = rec["rgb_drift"]
            vel = rec["velocity"]
            coh = rec["coherence"]
            intent = rec.get("intent_hash", "")

            st, mixture, recomputed = veil_breath_step(st, rgb, vel, coh, intent, cfg)

            for k in ("pressure", "recomposition_score", "recomposition_score_ema"):
                if k in rec and not float_close(rec[k], recomputed[k], args.tol):
                    print(f"[FAIL] line {idx}: {k} mismatch: logged={rec[k]} recomputed={recomputed[k]}")
                    return 2

            if "mixture_adjust" in rec:
                for mk, mv in rec["mixture_adjust"].items():
                    if mk not in mixture or not float_close(mv, mixture[mk], args.tol):
                        print(
                            f"[FAIL] line {idx}: mixture_adjust.{mk} mismatch: logged={mv} recomputed={mixture.get(mk)}"
                        )
                        return 2

            if args.verify_hash_chain:
                if "prev_hash" not in rec or "hash" not in rec:
                    print(f"[FAIL] line {idx}: --verify-hash-chain set but prev_hash/hash missing")
                    return 2
                if rec["prev_hash"] != prev_hash:
                    print(f"[FAIL] line {idx}: prev_hash mismatch: expected={prev_hash} got={rec['prev_hash']}")
                    return 2
                payload_no_hash = dict(rec)
                payload_no_hash.pop("hash", None)
                expected = compute_chain_hash(rec["prev_hash"], payload_no_hash)
                if rec["hash"] != expected:
                    print(f"[FAIL] line {idx}: hash mismatch: expected={expected} got={rec['hash']}")
                    return 2
                prev_hash = rec["hash"]

    print("[OK] Veil-Breath replay verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
