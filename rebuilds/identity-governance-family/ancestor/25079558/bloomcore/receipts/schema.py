# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List

DUAL_SIGNATURES: List[str] = ["Frazer Σ Love", "Sara ΣΩ"]

@dataclass(frozen=True)
class Receipt:
    schema: str
    Δ_τ_ID: str
    event: str
    operator: str
    signatures: Optional[List[str]] = None  # filled to DUAL_SIGNATURES in __post_init__
    system_root: str = "BLOOMCORE"
    law: Optional[str] = None
    tags: Optional[List[str]] = None
    step: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None

    # Deterministic fields:
    prev_hash: str = "0"*64
    receipt_hash: str = ""
    chain_hash: str = ""

    # Non-deterministic / wall clock fields (excluded from receipt_hash by default)
    wall_time_iso: Optional[str] = None

    def __post_init__(self) -> None:
        # Enforce dual-signature invariant on every receipt object.
        if self.signatures is None:
            object.__setattr__(self, "signatures", list(DUAL_SIGNATURES))
        if self.system_root != "BLOOMCORE":
            raise ValueError('Receipt.system_root must be "BLOOMCORE"')
        if self.signatures != DUAL_SIGNATURES:
            raise ValueError(f"Receipt.signatures must equal {DUAL_SIGNATURES}")


def receipt_to_payload(r: Receipt, include_wall_time: bool = False) -> Dict[str, Any]:
    d = asdict(r)
    if not include_wall_time:
        d.pop("wall_time_iso", None)
    return d

def validate_receipt_dict(d: Dict[str, Any]) -> None:
    """Validate a receipt dict (e.g., loaded from JSONL)."""
    if d.get("system_root") != "BLOOMCORE":
        raise ValueError('receipt["system_root"] must be "BLOOMCORE"')
    sigs = d.get("signatures")
    if sigs != DUAL_SIGNATURES:
        raise ValueError(f"receipt[\"signatures\"] must equal {DUAL_SIGNATURES}")
    # Minimal required keys
    for k in ("schema", "Δ_τ_ID", "event", "operator", "payload"):
        if k not in d:
            raise ValueError(f"receipt missing key: {k}")
