# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class Receipt:
    r_id: str
    ts: float
    kind: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: str

@dataclass(frozen=True)
class Command:
    kind: str
    command_id: str
    scope: str
    action: str
    params: Dict[str, Any]
    choice_hash: Optional[str] = None
    audit_hash: Optional[str] = None
    evidence_refs: Optional[list[str]] = None
