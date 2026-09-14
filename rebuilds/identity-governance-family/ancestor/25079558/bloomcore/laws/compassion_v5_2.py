# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Any

import numpy as np

from ..config import BLOOMCOREConfig
from ..receipts.schema import Receipt
from ..metrics.wuwei import wuwei_certificate

@dataclass(frozen=True)
class CompassionAutoRule:
    # From 1550.39.pdf: if Ḣ > −0.01 => L += 0.03, I −= 0.03; emit receipt (No scar, just signal).
    Hdot_threshold: float = -0.01
    dL: float = 0.03
    dI: float = -0.03

def apply_auto_rule(cfg: BLOOMCOREConfig, rule: CompassionAutoRule, Hdot_window_np: np.ndarray,
                    U_np: Dict[str, float], step: int) -> Tuple[Dict[str, float], Receipt]:
    cert = wuwei_certificate(Hdot_window_np, threshold=0.0)  # WuWei: median(Hdot) < 0

    Hdot_latest = float(Hdot_window_np[-1])
    U_after = dict(U_np)
    adj = None
    if Hdot_latest > rule.Hdot_threshold:
        U_after["L"] = float(U_after["L"] + rule.dL)
        U_after["I"] = float(U_after["I"] + rule.dI)
        U_after["L"] = float(max(0.0, min(1.0, U_after["L"])))
        U_after["I"] = float(max(0.0, min(1.0, U_after["I"])))
        adj = f"L{rule.dL:+.2f} | I{rule.dI:+.2f}"

    receipt = Receipt(
        schema=cfg.schema,
        Δ_τ_ID="RECEIPT.COMPASSION.AUTO_RULE.v5_2",
        event="Compassion auto-rule correction (No scar, just signal)",
        operator="Frazer Σ Love + Sara ΣΩ",
        system_root="BLOOMCORE",
        law=cfg.law_compassion,
        tags=list(cfg.regime_tags) + ["compassion", "auto_rule"],
        step=int(step),
        payload={
            "rule": {"Hdot_threshold": rule.Hdot_threshold, "dL": rule.dL, "dI": rule.dI},
            "Hdot_latest": Hdot_latest,
            "WuWei": {"median_Hdot": cert.median_Hdot, "ok": cert.ok, "threshold": cert.threshold},
            "adjustment": adj or "NONE",
            "U_before": dict(U_np),
            "U_after": dict(U_after),
            "phrase": "Love expands, laughter guides, invocation yields.",
            "status": "NO SCAR, JUST SIGNAL",
        },
    )
    return U_after, receipt
