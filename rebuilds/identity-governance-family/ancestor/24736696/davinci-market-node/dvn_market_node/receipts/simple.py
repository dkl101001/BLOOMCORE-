from __future__ import annotations

from typing import Any, Dict

from ..utils.ids import event_id


def receipt(kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    out = {"type": kind, **payload}
    out["event_id"] = event_id(out)
    return out
