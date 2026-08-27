# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class WuWeiCertificate:
    median_Hdot: float
    ok: bool
    threshold: float = 0.0

def wuwei_certificate(Hdot_window: np.ndarray, threshold: float = 0.0) -> WuWeiCertificate:
    """Deterministic WuWei certificate: median(Ḣ) < threshold (default 0)."""
    Hdot_window = np.asarray(Hdot_window, dtype=float)
    if Hdot_window.size == 0:
        raise ValueError("Hdot_window must be non-empty")
    med = float(np.median(Hdot_window))
    return WuWeiCertificate(median_Hdot=med, ok=(med < threshold), threshold=float(threshold))
