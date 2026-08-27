from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import math

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))

@dataclass(frozen=True)
class RSSConfig:
    # depth saturation
    cd_tau: float = 3.0
    eps: float = 1e-9

    # drift heuristics
    drift_window: int = 8
    drift_threshold: float = 0.35
    min_replays_for_ed: int = 2

    # internal linear mixing weights (must sum to 1 per group)
    alpha_tc: float = 0.45
    alpha_ed: float = 0.35
    alpha_cd: float = 0.20

    beta_dlc: float = 0.50
    beta_lbr: float = 0.30
    beta_hcs: float = 0.20

    gamma_ear: float = 0.35
    gamma_sdi: float = 0.45
    gamma_pmg: float = 0.20

    delta_ar: float = 0.34
    delta_rrs: float = 0.33
    delta_ac: float = 0.33

    epsw_rc: float = 0.40
    epsw_csi: float = 0.30
    epsw_ct: float = 0.30

    # composite weights (renormalized over applicable dims)
    w_T: float = 0.25
    w_L: float = 0.25
    w_A: float = 0.20
    w_M: float = 0.15
    w_C: float = 0.15

def normalize_base_metrics(base: Dict[str, float], cfg: RSSConfig) -> Dict[str, float]:
    norm: Dict[str, float] = {}
    norm["TC"] = clamp(base.get("TC", 0.0))
    norm["ED"] = clamp(base.get("ED", 1.0))
    cd = float(base.get("CD", 0.0))
    norm["CD"] = clamp(1.0 - math.exp(-cd / max(cfg.cd_tau, cfg.eps)))
    norm["DLC"] = clamp(base.get("DLC", 0.0))
    norm["LBR"] = clamp(base.get("LBR", 1.0))
    norm["HCS"] = clamp(base.get("HCS", 0.0))
    norm["EAR"] = clamp(base.get("EAR", 0.0))
    norm["SDI"] = clamp(base.get("SDI", 0.0))
    norm["PMG"] = clamp(base.get("PMG", 0.0))

    for k in ("AR", "RRS", "AC", "RC", "CSI", "CT"):
        if k in base:
            norm[k] = clamp(base[k])
    return norm
