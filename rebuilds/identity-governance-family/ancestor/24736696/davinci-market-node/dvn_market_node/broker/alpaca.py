from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import Broker
from ..types import ExecutionResult, OrderIntent


@dataclass
class AlpacaBroker(Broker):
    """Alpaca broker adapter.

    Execution is real (paper or live depending on credentials + latch).

    Required env:
      - APCA_API_KEY_ID
      - APCA_API_SECRET_KEY
      - APCA_API_BASE_URL (paper default)

    Live enable latch:
      - DVN_LIVE_ENABLE=1

    NOTE: This ships as an execution-capable adapter. You own strategy inputs.
    """

    base_url: str
    key_id: str
    secret_key: str
    venue: str = "alpaca"

    @staticmethod
    def from_env() -> "AlpacaBroker":
        key_id = os.environ.get("APCA_API_KEY_ID", "")
        secret = os.environ.get("APCA_API_SECRET_KEY", "")
        base = os.environ.get("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
        return AlpacaBroker(base_url=base, key_id=key_id, secret_key=secret)

    def _enabled(self) -> bool:
        # We allow paper without latch; live requires latch.
        base = (self.base_url or "").lower()
        is_live = ("paper" not in base) and ("paper-api" not in base)
        if not is_live:
            return True
        return os.environ.get("DVN_LIVE_ENABLE", "0") == "1"

    def health(self) -> Dict[str, Any]:
        ok = bool(self.key_id and self.secret_key)
        return {"venue": self.venue, "ok": ok, "base_url": self.base_url, "enabled": self._enabled()}

    def submit(self, intent: OrderIntent) -> ExecutionResult:
        if not (self.key_id and self.secret_key):
            return {"ok": False, "venue": self.venue, "order_id": None, "status": "missing_keys", "detail": {}}
        if not self._enabled():
            return {"ok": False, "venue": self.venue, "order_id": None, "status": "live_not_enabled", "detail": {"hint": "Set DVN_LIVE_ENABLE=1 for live base URL."}}

        # Lazy import to keep install flexible.
        try:
            import requests
        except Exception as e:
            return {"ok": False, "venue": self.venue, "order_id": None, "status": "missing_requests", "detail": {"error": repr(e)}}

        headers = {
            "APCA-API-KEY-ID": self.key_id,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json",
        }

        body: Dict[str, Any] = {
            "symbol": intent["symbol"],
            "qty": str(intent["qty"]),
            "side": intent["side"],
            "type": intent["order_type"],
            "time_in_force": intent["tif"],
        }
        if intent["order_type"] == "limit" and intent.get("limit_price") is not None:
            body["limit_price"] = str(intent["limit_price"])

        try:
            r = requests.post(f"{self.base_url}/v2/orders", headers=headers, json=body, timeout=15)
            if r.status_code >= 300:
                return {"ok": False, "venue": self.venue, "order_id": None, "status": f"http_{r.status_code}", "detail": {"body": r.text}}
            j = r.json()
            return {"ok": True, "venue": self.venue, "order_id": j.get("id"), "status": j.get("status", "submitted"), "detail": j}
        except Exception as e:
            return {"ok": False, "venue": self.venue, "order_id": None, "status": "exception", "detail": {"error": repr(e)}}
