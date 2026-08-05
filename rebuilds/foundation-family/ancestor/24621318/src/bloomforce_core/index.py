from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from .ledger import Receipt


@dataclass
class LedgerIndex:
    last_hash_by_kind: Dict[str, str] = field(default_factory=dict)
    last_rid_by_kind: Dict[str, str] = field(default_factory=dict)

    last_step_hash: Optional[str] = None
    last_step_rid: Optional[str] = None
    last_step_tick: Optional[int] = None
    last_step_x: Optional[float] = None
    last_step_force: Optional[float] = None
    last_step_gate: Optional[float] = None

    def ingest(self, r: Receipt) -> None:
        k = str(r.kind)
        self.last_hash_by_kind[k] = str(r.hash)
        self.last_rid_by_kind[k] = str(r.r_id)

        if k == "BLOOMFORCE_STEP":
            self.last_step_hash = str(r.hash)
            self.last_step_rid = str(r.r_id)
            p = r.payload or {}
            try:
                self.last_step_tick = int(p.get("tick")) if p.get("tick") is not None else None
            except Exception:
                self.last_step_tick = None
            try:
                st = p.get("state") or {}
                self.last_step_x = float(st.get("x")) if st.get("x") is not None else None
                self.last_step_force = float(st.get("last_force")) if st.get("last_force") is not None else None
            except Exception:
                self.last_step_x = None
                self.last_step_force = None
            try:
                self.last_step_gate = float(p.get("gate")) if p.get("gate") is not None else None
            except Exception:
                self.last_step_gate = None

    def summary(self) -> Dict[str, Any]:
        return {
            "last_hash_by_kind": dict(self.last_hash_by_kind),
            "last_rid_by_kind": dict(self.last_rid_by_kind),
            "last_step": {
                "hash": self.last_step_hash,
                "rid": self.last_step_rid,
                "tick": self.last_step_tick,
                "x": self.last_step_x,
                "last_force": self.last_step_force,
                "gate": self.last_step_gate,
            },
        }
