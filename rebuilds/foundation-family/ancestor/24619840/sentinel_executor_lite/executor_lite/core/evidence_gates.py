# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

DEFAULT_HARD_EVIDENCE_KINDS: Set[str] = {
    "BINARY_IOC_CONFIRMED",
    "HONEYTOKEN_TRIP",
    "INTEGRITY_BREAK_CONFIRMED",
}

DEFAULT_COMMANDS_REQUIRING_EVIDENCE: Set[str] = {
    "EXEC_ISOLATE_ENTER",
    "EXEC_SHUTDOWN_REQUEST",
}

@dataclass
class EvidenceGateSet:
    hard_evidence_kinds: Set[str] = field(default_factory=lambda: set(DEFAULT_HARD_EVIDENCE_KINDS))
    commands_requiring_evidence: Set[str] = field(default_factory=lambda: set(DEFAULT_COMMANDS_REQUIRING_EVIDENCE))

    def command_requires_evidence(self, cmd_kind: str) -> bool:
        return str(cmd_kind).upper() in self.commands_requiring_evidence

def check_evidence(
    *,
    gates: EvidenceGateSet,
    cmd_kind: str,
    evidence_refs: list[str] | None,
    ledger_hashes_present: Set[str],
    ledger_kinds_present: Set[str],
) -> tuple[bool, str]:
    cmd_kind = str(cmd_kind).upper()
    if not gates.command_requires_evidence(cmd_kind):
        return True, "OK_NOT_REQUIRED"

    if any(k in ledger_kinds_present for k in gates.hard_evidence_kinds):
        return True, "OK_GLOBAL_EVIDENCE_PRESENT"

    refs = [str(x) for x in (evidence_refs or []) if x]
    if not refs:
        return False, "MISSING_EVIDENCE_REFS"
    if any(r in ledger_hashes_present for r in refs):
        return True, "OK_REF_MATCH"
    return False, "EVIDENCE_REFS_NOT_FOUND"
