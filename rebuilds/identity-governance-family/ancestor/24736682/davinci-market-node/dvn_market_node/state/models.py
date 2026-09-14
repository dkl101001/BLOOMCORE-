from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple

from ..signals import RegimeState


DriftStatus = Literal["OK", "WARN", "BREAK"]


@dataclass(frozen=True)
class StateKey:
    """Canonical identifier for strategy state carry across pulses."""

    strategy_id: str
    mode: str
    universe_id: str

    def to_str(self) -> str:
        return f"{self.strategy_id}::{self.mode}::{self.universe_id}"


@dataclass
class SourceClaim:
    src: Literal["memory", "compendium", "receipts"]
    as_of_eq_id: Optional[str]
    prev_state: Optional[RegimeState]
    payload: Dict[str, Any]


@dataclass
class ResolvedState:
    state_key: StateKey
    as_of_eq_id: Optional[str]
    prev_state: RegimeState
    invalidation_level: Optional[float]
    last_intensity: float
    last_reason: str
    receipt_tip_event_id: Optional[str]
    compendium_hash: Optional[str]
    drift_status: DriftStatus
    drift_reasons: List[str]
    claims: List[SourceClaim]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_key": self.state_key.to_str(),
            "as_of_eq_id": self.as_of_eq_id,
            "prev_state": self.prev_state,
            "invalidation_level": self.invalidation_level,
            "last_intensity": self.last_intensity,
            "last_reason": self.last_reason,
            "receipt_tip_event_id": self.receipt_tip_event_id,
            "compendium_hash": self.compendium_hash,
            "drift": {"status": self.drift_status, "reasons": list(self.drift_reasons)},
            "claims": [
                {
                    "src": c.src,
                    "as_of_eq_id": c.as_of_eq_id,
                    "prev_state": c.prev_state,
                    "payload": c.payload,
                }
                for c in self.claims
            ],
        }


def stable_hash(obj: Any) -> str:
    """Stable SHA256 hash of a JSON-serializable object."""
    import hashlib

    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
