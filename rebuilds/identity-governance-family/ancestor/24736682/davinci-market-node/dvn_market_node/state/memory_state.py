from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..signals import RegimeState
from .models import StateKey


_MEM: Dict[str, Dict[str, Any]] = {}


def read_memory(key: StateKey) -> Optional[Dict[str, Any]]:
    return _MEM.get(key.to_str())


def write_memory(key: StateKey, payload: Dict[str, Any]) -> None:
    _MEM[key.to_str()] = dict(payload)
