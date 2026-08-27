"""world_engine.authority_adapter

Ship-safe authority boundary.

World Engine (OSS) ships:
  - a tamper-evident ledger (BLOOMCORE + Echoshell)
  - an operator terminal (Node 0)
  - interface integrity monitoring (MIRRORSEED interface governor)
  - optional telemetry sampling (Node 1)
  - scheduled contradiction cycle receipts (MIRRORSEED.CYCLE.vΩ)

World Engine (OSS) does NOT ship:
  - coherence computation
  - ECA vector bases / canonical dimensions
  - regime selection
  - adaptive gates / thresholds
  - holographic coupling logic

Those mechanisms belong in private/provisional packages.

This module defines the *shape* of an authority adapter so you can plug
in your private governor without leaking it into the public tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass(frozen=True)
class AuthorityDecision:
    """Return value from an external/private authority.

    action:
      - "ALLOW"    : proceed (carrier continues)
      - "HOLD"     : do not commit / pause
      - "ROLLBACK" : request rollback to a known snapshot id
      - "HALT"     : hard stop

    note/meta are for audit only; do not embed mechanism details here.
    """

    action: str
    note: str = ""
    meta: Dict[str, Any] = None
    target_snapshot: Optional[str] = None


class AuthorityAdapter(Protocol):
    """Pluggable authority boundary.

    Implement this in a *separate* private repo/package.
    """

    def observe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Project state into an observation payload.

        OSS guidance: keep this a plain mapping.
        Private guidance: this is where your ECA/holographic logic may live.
        """
        ...

    def decide(self, observation: Dict[str, Any]) -> AuthorityDecision:
        """Return an authority decision.

        Must be deterministic given the observation *or* be fully auditable
        via your private receipts. The OSS surface does not care.
        """
        ...


class NullAuthority:
    """Default ship-safe adapter: always allows; no hidden logic."""

    def observe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"state_keys": sorted(list(state.keys()))}

    def decide(self, observation: Dict[str, Any]) -> AuthorityDecision:
        return AuthorityDecision(action="ALLOW", note="NullAuthority")
