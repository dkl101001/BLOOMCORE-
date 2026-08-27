from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .canonical import QuantizeSpec, quantize_payload, hash_receipt


@dataclass(frozen=True)
class ReceiptMeta:
    module: str = "bloomcore_nlse_antigovernor"
    receipt_type: str = "DLD.ANTI_GOVERNOR_CHECK.v1"
    qspec: QuantizeSpec = QuantizeSpec()


def build_anti_governor_receipts(
    *,
    V_prev: List[float],
    V_curr: List[float],
    dV: List[float],
    tau_export: List[float],
    violation: List[bool],
    meta: Optional[Dict[str, Any]] = None,
    receipt_meta: ReceiptMeta = ReceiptMeta(),
) -> List[Dict[str, Any]]:
    """Host-side receipt build: quantize metrics -> hash -> attach."""
    meta = meta or {}

    if not (len(V_prev) == len(V_curr) == len(dV) == len(tau_export) == len(violation)):
        raise ValueError("Receipt series length mismatch.")

    out: List[Dict[str, Any]] = []
    for i in range(len(dV)):
        payload: Dict[str, Any] = {
            "type": receipt_meta.receipt_type,
            "step": int(i),
            "V_prev": float(V_prev[i]),
            "V_curr": float(V_curr[i]),
            "dV": float(dV[i]),
            "tau_export": float(tau_export[i]),
            "violation": bool(violation[i]),
            "meta": {
                "module": receipt_meta.module,
                "quantize": {
                    "scheme": receipt_meta.qspec.scheme,
                    "decimals": receipt_meta.qspec.decimals,
                    "nan_sentinel": receipt_meta.qspec.nan_sentinel,
                },
                **meta,
            },
        }

        payload_for_hash = quantize_payload(
            payload,
            receipt_meta.qspec,
            float_keys=["V_prev", "V_curr", "dV", "tau_export"],
        )
        payload["hash"] = hash_receipt(payload_for_hash)
        out.append(payload)

    return out
