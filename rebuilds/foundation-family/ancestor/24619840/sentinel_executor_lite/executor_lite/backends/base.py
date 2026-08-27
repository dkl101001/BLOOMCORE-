# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol

@dataclass
class BackendResult:
    ok: bool
    detail: Dict[str, Any]

class Backend(Protocol):
    name: str
    def execute(self, cmd_kind: str, payload: Dict[str, Any]) -> BackendResult: ...
