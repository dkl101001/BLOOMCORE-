# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

REQUIRED_TOP_KEYS = {"schema_version", "ts", "event", "role", "payload"}

KNOWN_EVENTS: Set[str] = {
    "kernel.start",
    "role.planner",
    "role.critic",
    "kernel.revise",
    "kernel.decision",
    "role.executor",
    "kernel.end",
}

@dataclass
class ValidateIssue:
    file: str
    line: int
    event: Optional[str]
    severity: str  # ERROR|WARN
    message: str

@dataclass
class ValidateReport:
    ok: bool = True
    issues: List[ValidateIssue] = field(default_factory=list)

    def add(self, issue: ValidateIssue) -> None:
        self.issues.append(issue)
        if issue.severity == "ERROR":
            self.ok = False

def validate_file(path: Path, *, strict: bool = False, schema_version: Optional[str] = None) -> ValidateReport:
    rep = ValidateReport()
    saw_end = False

    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except Exception as e:
                rep.add(ValidateIssue(str(path), idx, None, "ERROR", f"Invalid JSON: {e}"))
                continue

            missing = REQUIRED_TOP_KEYS - set(evt.keys())
            if missing:
                rep.add(ValidateIssue(str(path), idx, evt.get("event"), "ERROR", f"Missing top-level keys: {sorted(list(missing))}"))
                continue

            sv = evt.get("schema_version")
            if not isinstance(sv, str) or not sv:
                rep.add(ValidateIssue(str(path), idx, evt.get("event"), "ERROR", "schema_version must be a non-empty string."))
                continue
            if schema_version is not None and sv != schema_version:
                rep.add(ValidateIssue(str(path), idx, evt.get("event"), "ERROR", f"schema_version mismatch: expected '{schema_version}' got '{sv}'"))
                continue

            ev = evt.get("event")
            if strict and ev not in KNOWN_EVENTS:
                rep.add(ValidateIssue(str(path), idx, ev, "ERROR", f"Unknown event in strict mode: {ev}"))
            if ev == "kernel.end":
                saw_end = True

    if strict and not saw_end:
        rep.add(ValidateIssue(str(path), -1, None, "ERROR", "Strict mode requires kernel.end event."))

    return rep

def validate_paths(paths: List[Path], *, strict: bool = False, schema_version: Optional[str] = None) -> ValidateReport:
    rep = ValidateReport()
    for p in paths:
        if p.is_dir():
            for f in sorted(p.glob("*.jsonl")):
                r = validate_file(f, strict=strict, schema_version=schema_version)
                rep.ok = rep.ok and r.ok
                rep.issues.extend(r.issues)
        else:
            r = validate_file(p, strict=strict, schema_version=schema_version)
            rep.ok = rep.ok and r.ok
            rep.issues.extend(r.issues)
    return rep
