from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base import Broker
from ..types import ExecutionResult, OrderIntent


@dataclass
class PaperBroker(Broker):
    venue: str = "paper"

    def submit(self, intent: OrderIntent) -> ExecutionResult:
        # Non-executable simulation sink; logs order-id deterministically from intent_id.
        return {
            "ok": True,
            "venue": self.venue,
            "order_id": f"PAPER-{intent['intent_id'][:12]}",
            "status": "accepted",
            "detail": {"intent": intent},
        }

    def health(self) -> Dict[str, Any]:
        return {"venue": self.venue, "ok": True}
