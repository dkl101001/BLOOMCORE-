from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
from .utils import now_ts, hash_obj


@dataclass(frozen=True)
class Receipt:
    r_id: str
    ts: float
    kind: str
    payload: Dict
    prev_hash: str
    hash: str


@dataclass
class Ledger:
    receipts: list[Receipt] = field(default_factory=list)

    def last_hash(self) -> str:
        return self.receipts[-1].hash if self.receipts else "GENESIS"

    def append(self, kind: str, payload: Dict, *, ts: Optional[float] = None) -> Receipt:
        if ts is None:
            ts = now_ts()
        prev = self.last_hash()
        core = {"ts": ts, "kind": kind, "payload": payload, "prev_hash": prev}
        h = hash_obj(core)
        r = Receipt(r_id=f"{kind}:{h[:16]}", ts=ts, kind=kind, payload=payload, prev_hash=prev, hash=h)
        self.receipts.append(r)
        return r

    def verify_chain(self) -> bool:
        prev = "GENESIS"
        for r in self.receipts:
            core = {"ts": r.ts, "kind": r.kind, "payload": r.payload, "prev_hash": prev}
            if hash_obj(core) != r.hash:
                return False
            if r.prev_hash != prev:
                return False
            prev = r.hash
        return True
