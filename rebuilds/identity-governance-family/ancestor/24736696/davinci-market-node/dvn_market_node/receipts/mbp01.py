from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..utils.ids import event_id


@dataclass
class MBP01Receipt:
    dt: str
    eq_id: str
    facts: List[str]
    sentinel_tripwires: List[str]
    mirrorseed_integrity: str
    dreamloop: str
    compendium_semver: Dict[str, str]
    schema: str = "MBP-01.v1"
    kind: str = "BLOOMCORE.RECEIPT"

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "Δ^τ_ID": f"{self.kind}.{self.eq_id}",
            "schema": self.schema,
            "timestamp": self.dt,
            "eq_id": self.eq_id,
            "facts": list(self.facts),
            "sentinel_tripwires": list(self.sentinel_tripwires),
            "mirrorseed_integrity": self.mirrorseed_integrity,
            "dreamloop": self.dreamloop,
            "compendium_semver": dict(self.compendium_semver),
        }
        payload["event_id"] = event_id(payload)
        return payload
