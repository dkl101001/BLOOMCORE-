# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
import json, sys, hashlib
from pathlib import Path
from bloomcore.receipts.canonical import canonical_json_bytes, sha256_hex

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python verify_release.py <receipts.jsonl>")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"missing: {p}")
        return 2
    prev = "0"*64
    n = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        # verify chain
        rh = rec["receipt_hash"]
        ch = rec["chain_hash"]
        calc = hashlib.sha256((prev + rh).encode("utf-8")).hexdigest()
        if calc != ch:
            print(f"chain mismatch at line {n}: expected {calc}, got {ch}")
            return 1
        prev = ch
        n += 1
    print(f"OK: {n} receipts; final_chain_hash={prev}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
