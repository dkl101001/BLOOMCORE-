# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, List

@dataclass(frozen=True)
class Receipt:
    r_id: str
    ts: float
    kind: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: str

@dataclass(frozen=True)
class ProposedCommand:
    command_id: str
    scope: str
    action: str
    params: Dict[str, Any]
    evidence_refs: Optional[List[str]] = None
    choice_hash: Optional[str] = None
    audit_hash: Optional[str] = None

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reasons: List[str]
    constraints: Dict[str, Any]
