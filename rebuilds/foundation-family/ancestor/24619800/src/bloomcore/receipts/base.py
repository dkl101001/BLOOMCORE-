from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import uuid
import datetime


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class BaseReceipt:
    dtau_id: str
    schema_version: str
    engine_version: str
    timestamp: str
    anchors: List[str]
    payload: Dict[str, Any]

    @classmethod
    def new(
        cls,
        schema_version: str,
        engine_version: str,
        anchors: List[str],
        payload: Dict[str, Any],
    ) -> "BaseReceipt":
        return cls(
            dtau_id=f"Δ^τ.{uuid.uuid4().hex[:8]}",
            schema_version=schema_version,
            engine_version=engine_version,
            timestamp=_now_iso(),
            anchors=anchors,
            payload=payload,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dtau_id": self.dtau_id,
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "timestamp": self.timestamp,
            "anchors": list(self.anchors),
            "payload": dict(self.payload),
        }
