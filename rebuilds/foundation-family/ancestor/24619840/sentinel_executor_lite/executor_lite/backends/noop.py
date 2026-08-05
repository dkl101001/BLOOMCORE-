# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base import BackendResult

@dataclass
class NoopBackend:
    name: str = "noop"
    cfg: Dict[str, Any] | None = None

    def execute(self, cmd_kind: str, payload: Dict[str, Any]) -> BackendResult:
        return BackendResult(ok=True, detail={"backend": self.name, "cmd_kind": cmd_kind, "note": "noop"})
