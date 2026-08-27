# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import os
import re
import signal
from dataclasses import dataclass
from typing import Any, Dict, List

from .base import BackendResult

_SIGNAL_MAP = {"STOP": signal.SIGSTOP, "CONT": signal.SIGCONT, "TERM": signal.SIGTERM, "KILL": signal.SIGKILL}

def _compile(res: List[str]) -> List[re.Pattern]:
    out = []
    for s in res:
        try:
            out.append(re.compile(s))
        except re.error:
            continue
    return out

def _pid_cmdline(pid: int) -> str:
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            raw = f.read().replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
        return raw
    except Exception:
        return ""

@dataclass
class ProcessBackend:
    name: str = "process"
    allow_pids: List[int] | None = None
    allow_cmd_regex: List[str] | None = None
    signal_map: Dict[str, str] | None = None

    def __post_init__(self) -> None:
        self.allow_pids = list(self.allow_pids or [])
        self.allow_cmd_regex = list(self.allow_cmd_regex or [])
        self.signal_map = dict(self.signal_map or {"PAUSE": "STOP", "RESUME": "CONT", "SHUTDOWN": "TERM"})
        self._rx = _compile(self.allow_cmd_regex)

    def _allowed(self, pid: int) -> bool:
        if self.allow_pids and pid in self.allow_pids:
            return True
        if self._rx:
            cmd = _pid_cmdline(pid)
            return any(r.search(cmd) for r in self._rx)
        return False

    def execute(self, cmd_kind: str, payload: Dict[str, Any]) -> BackendResult:
        pid = int(payload.get("pid", -1))
        op = str(payload.get("op", "")).upper()
        if pid <= 1:
            return BackendResult(ok=False, detail={"reason": "invalid_pid", "pid": pid})
        if not self._allowed(pid):
            return BackendResult(ok=False, detail={"reason": "pid_not_allowed", "pid": pid})

        sig_name = str(self.signal_map.get(op, "")).upper()
        sig = _SIGNAL_MAP.get(sig_name)
        if sig is None:
            return BackendResult(ok=False, detail={"reason": "unknown_signal", "op": op, "sig_name": sig_name})

        try:
            os.kill(pid, sig)
            return BackendResult(ok=True, detail={"pid": pid, "op": op, "sig": sig_name})
        except ProcessLookupError:
            return BackendResult(ok=False, detail={"reason": "pid_not_found", "pid": pid})
        except PermissionError:
            return BackendResult(ok=False, detail={"reason": "permission_denied", "pid": pid})
        except Exception as e:
            return BackendResult(ok=False, detail={"reason": "error", "pid": pid, "err": str(e)})
