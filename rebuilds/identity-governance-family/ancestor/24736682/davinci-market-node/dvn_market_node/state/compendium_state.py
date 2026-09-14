from __future__ import annotations

from typing import Any, Dict, Optional

from .models import StateKey, stable_hash


def _get_bucket(st: Dict[str, Any]) -> Dict[str, Any]:
    bucket = st.get("strategy_state")
    if not isinstance(bucket, dict):
        bucket = {}
        st["strategy_state"] = bucket
    return bucket


def read_compendium_claim(state: Dict[str, Any], key: StateKey) -> Optional[Dict[str, Any]]:
    bucket = _get_bucket(state)
    val = bucket.get(key.to_str())
    if isinstance(val, dict):
        return val
    return None


def write_compendium_claim(state: Dict[str, Any], key: StateKey, payload: Dict[str, Any]) -> None:
    bucket = _get_bucket(state)
    bucket[key.to_str()] = dict(payload)
    state["compendium_state_hash"] = stable_hash(state)
