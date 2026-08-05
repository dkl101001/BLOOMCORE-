# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Optional

from .types import ProposedCommand, Decision

class SignalProvider(Protocol):
    """Optional: attach domain signals to a proposal (ECA-neutral seam)."""
    def get_signals(self, proposal: ProposedCommand) -> Dict[str, Any]: ...

class Policy(Protocol):
    def decide(self, proposal: ProposedCommand, signals: Optional[Dict[str, Any]] = None) -> Decision: ...

@dataclass
class AllowlistPolicy:
    policy_id: str
    allow_scopes: List[str]
    allow_actions: List[str]
    deny_actions: List[str]
    require_evidence_for_actions: List[str]
    max_params_bytes: int = 65536

    def decide(self, proposal: ProposedCommand, signals: Optional[Dict[str, Any]] = None) -> Decision:
        reasons: List[str] = []
        constraints: Dict[str, Any] = {"policy_id": self.policy_id}

        if proposal.scope not in self.allow_scopes:
            reasons.append(f"scope_not_allowed:{proposal.scope}")
        if proposal.action in self.deny_actions:
            reasons.append(f"action_denied:{proposal.action}")
        if proposal.action not in self.allow_actions:
            reasons.append(f"action_not_allowed:{proposal.action}")

        # evidence requirement
        if proposal.action in self.require_evidence_for_actions:
            if not proposal.evidence_refs:
                reasons.append("evidence_required_missing")

        # size guard
        import json
        try:
            b = len(json.dumps(proposal.params, ensure_ascii=False).encode("utf-8"))
        except Exception:
            b = self.max_params_bytes + 1
        if b > self.max_params_bytes:
            reasons.append(f"params_too_large:{b}>{self.max_params_bytes}")

        allowed = len(reasons) == 0
        if allowed:
            constraints["max_runtime_s"] = 30
        return Decision(allowed=allowed, reasons=reasons, constraints=constraints)
