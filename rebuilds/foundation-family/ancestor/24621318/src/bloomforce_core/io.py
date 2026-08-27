from __future__ import annotations

from typing import Iterable
import json, os
from .ledger import Ledger, Receipt
from .utils import canonical_json


def receipt_to_dict(r: Receipt) -> dict:
    return {
        "r_id": r.r_id,
        "ts": r.ts,
        "kind": r.kind,
        "payload": r.payload,
        "prev_hash": r.prev_hash,
        "hash": r.hash,
    }


def dict_to_receipt(d: dict) -> Receipt:
    required = ("r_id", "ts", "kind", "payload", "prev_hash", "hash")
    missing = [k for k in required if k not in d]
    if missing:
        raise ValueError(f"receipt missing keys: {missing}")
    return Receipt(
        r_id=str(d["r_id"]),
        ts=float(d["ts"]),
        kind=str(d["kind"]),
        payload=dict(d["payload"]) if isinstance(d["payload"], dict) else {"payload": d["payload"]},
        prev_hash=str(d["prev_hash"]),
        hash=str(d["hash"]),
    )


def save_ledger_jsonl(ledger: Ledger, path: str, *, overwrite: bool = True) -> None:
    path = os.path.abspath(path)
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in ledger.receipts:
            f.write(canonical_json(receipt_to_dict(r)) + "\n")


def load_ledger_jsonl(path: str, *, strict: bool = True) -> Ledger:
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    led = Ledger()
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception as e:
                raise ValueError(f"invalid json at line {ln}: {e}") from e
            led.receipts.append(dict_to_receipt(d))
    if strict and not led.verify_chain():
        raise ValueError("ledger verification failed (chain broken or tampered hashes)")
    return led


def iter_receipts_jsonl(path: str) -> Iterable[Receipt]:
    path = os.path.abspath(path)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield dict_to_receipt(json.loads(line))
