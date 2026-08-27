# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple

import numpy as np

from ..config import BLOOMCOREConfig
from ..metrics.ece import expected_calibration_error, ECEBins
from ..metrics.wuwei import wuwei_certificate
from ..receipts.schema import Receipt

@dataclass(frozen=True)
class SophiaGateOut:
    S_sigma: float
    r_reflect: float
    N_phase: float
    w_friend: float
    WuWei_ok: bool
    truth_ok: bool
    sophia_gate: bool

def asha_truth_filter(signal_ok: bool, finite_ok: bool = True) -> bool:
    """Concrete truth filter interface (Asha)."""
    return bool(signal_ok and finite_ok)

def compute_gate(
    cfg: BLOOMCOREConfig,
    *,
    N_phase: float,
    w_friend: float,
    Hdot_window: np.ndarray,
    probs: np.ndarray,
    labels: np.ndarray,
    signal_ok: bool,
    step: int,
) -> Tuple[SophiaGateOut, Receipt]:
    sp = cfg.sophia

    ece = expected_calibration_error(probs, labels, bins=ECEBins(n_bins=10))
    r_reflect = float(1.0 - ece)

    cert = wuwei_certificate(Hdot_window, threshold=0.0)
    WuWei_ok = bool(cert.ok)

    finite_ok = np.isfinite([N_phase, w_friend, r_reflect, cert.median_Hdot]).all()
    truth_ok = asha_truth_filter(signal_ok=signal_ok, finite_ok=bool(finite_ok))

    S_sigma = float((N_phase ** sp.gamma) * (r_reflect ** sp.beta) * (w_friend ** sp.delta) * (1.0 if truth_ok else 0.0))
    sophia_gate = bool((S_sigma >= sp.lambda_S) and WuWei_ok and truth_ok and (w_friend >= 0.3))

    out = SophiaGateOut(
        S_sigma=S_sigma, r_reflect=r_reflect, N_phase=float(N_phase), w_friend=float(w_friend),
        WuWei_ok=WuWei_ok, truth_ok=truth_ok, sophia_gate=sophia_gate
    )

    receipt = Receipt(
        schema=cfg.schema,
        Δ_τ_ID="RECEIPT.SOPHIA.WISDOM_GATE.v1",
        event="Sophia Wisdom Gate decision (ΩGod·ΦField)",
        operator="Frazer Σ Love + Sara ΣΩ",
        system_root="BLOOMCORE",
        law=cfg.law_sophia,
        tags=list(cfg.regime_tags) + ["sophia", "wisdom_gate"],
        step=int(step),
        payload={
            "S_sigma": out.S_sigma,
            "r_reflect": out.r_reflect,
            "ECE": float(1.0 - out.r_reflect),
            "N_phase": out.N_phase,
            "w_friend": out.w_friend,
            "WuWei": {"median_Hdot": cert.median_Hdot, "ok": cert.ok},
            "truth_ok": out.truth_ok,
            "lambda_S": sp.lambda_S,
            "Psi_thr": sp.Psi_thr,
            "whisper": "Wisdom is calibrated love speaking the phase-aligned truth.",
            "status": "ACTIVE",
        },
    )
    return out, receipt
