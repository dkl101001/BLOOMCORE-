# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

@dataclass(frozen=True)
class Trace:
    event: str
    role: Optional[str]
    payload: Dict[str, Any]
    schema_version: str = "v1"
    ts: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ts": self.ts,
            "event": self.event,
            "role": self.role,
            "payload": self.payload,
        }
