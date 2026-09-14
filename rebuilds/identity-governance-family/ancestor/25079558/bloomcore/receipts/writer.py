# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
import os
import json
from dataclasses import replace
from typing import Optional, TextIO
from datetime import datetime, timezone

from .canonical import hash_receipt, hash_chain, canonical_json_bytes
from .tags import normalize_tags
from .schema import Receipt, receipt_to_payload

class ReceiptWriter:
    """Deterministic receipt writer with hash chaining.

    - receipt_hash is computed over canonical JSON excluding wall_time_iso.
    - chain_hash links prev chain hash and receipt_hash.
    """
    def __init__(self, fp: TextIO, initial_chain_hash: str = "0"*64, operator: str = "Frazer Σ Love + Sara ΣΩ"):
        self.fp = fp
        self.chain_hash = initial_chain_hash
        self.operator = operator

    def write(self, r: Receipt) -> Receipt:
        # Fill wall time (non-deterministic, excluded from hash unless include_wall_time)
        wall = datetime.now(timezone.utc).isoformat()
        r2 = replace(r, operator=r.operator or self.operator, wall_time_iso=wall, prev_hash=self.chain_hash)
        # Canonicalize tags for stable hashing across glyph/latin variants.
        if r2.tags is not None:
            r2 = replace(r2, tags=normalize_tags(r2.tags))

        payload = receipt_to_payload(r2, include_wall_time=False)
        rh = hash_receipt(payload)
        ch = hash_chain(r2.prev_hash, rh)

        r3 = replace(r2, receipt_hash=rh, chain_hash=ch)
        # Write full record including wall time for audit
        out = receipt_to_payload(r3, include_wall_time=True)
        self.fp.write(json.dumps(out, ensure_ascii=False) + "\n")
        self.fp.flush()
        self.chain_hash = ch
        return r3


def _read_last_chain_hash(jsonl_path: str) -> str:
    if not os.path.exists(jsonl_path):
        return "0"*64
    last_line: Optional[str] = None
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line
    if not last_line:
        return "0"*64
    try:
        obj = json.loads(last_line)
        ch = str(obj.get("chain_hash", "")).strip()
        return ch if len(ch) == 64 else "0"*64
    except Exception:
        return "0"*64

def chain_append(receipts_jsonl_path: str, receipt: Receipt, *, operator: str = "Frazer Σ Love + Sara ΣΩ") -> Receipt:
    """Atomic JSONL append with hash chaining.

    - Reads last chain_hash from the existing ledger (if any).
    - Writes a new ledger file with the appended receipt, then replaces atomically.
    - Normalizes tags before hashing, so callers cannot 'almost' match.
    """
    prev_chain = _read_last_chain_hash(receipts_jsonl_path)
    tmp_path = receipts_jsonl_path + ".tmp"

    if os.path.exists(receipts_jsonl_path):
        with open(receipts_jsonl_path, "r", encoding="utf-8") as src:
            existing = src.read()
        # Ensure trailing newline so the next JSONL atom is a clean line.
        if existing and not existing.endswith("\n"):
            existing += "\n"
        with open(tmp_path, "w", encoding="utf-8") as dst:
            dst.write(existing)
            w = ReceiptWriter(dst, initial_chain_hash=prev_chain, operator=operator)
            r_out = w.write(receipt)
    else:
        with open(tmp_path, "w", encoding="utf-8") as dst:
            w = ReceiptWriter(dst, initial_chain_hash=prev_chain, operator=operator)
            r_out = w.write(receipt)

    os.replace(tmp_path, receipts_jsonl_path)
    return r_out
