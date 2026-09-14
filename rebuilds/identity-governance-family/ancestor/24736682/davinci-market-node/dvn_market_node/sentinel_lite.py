from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


DEFAULT_TRIPWIRES = [
    "OPEN_gap_vol>+20%",
    "VIX_futs>+5%d/d",
    "10Y_rate_spike",
    "WTI<floor",
    "REL.coherence<0.40",
    "REL.mirror_trust<0.40",
    "REL.fracture>=0.60",
]


@dataclass
class DriftLogger:
    status: str = "armed"
    retention_days: int = 30
    last_event: str = "none"
    next_checks: List[str] = None

    def to_dict(self, eq_id: str) -> Dict[str, Any]:
        return {
            "status": self.status,
            "retention_days": self.retention_days,
            "last_event": self.last_event,
            "next_checks": self.next_checks or ["10:15", "11:45", "13:30"],
            "eq_id": eq_id,
        }
