from __future__ import annotations

from typing import Dict
from .normalize import RSSConfig, clamp

def compute_subscores(norm: Dict[str, float], cfg: RSSConfig, applicability: Dict[str, bool]) -> Dict[str, float]:
    S: Dict[str, float] = {}

    S_T = (
        cfg.alpha_tc * norm.get("TC", 0.0)
        + cfg.alpha_ed * (1.0 - norm.get("ED", 1.0))
        + cfg.alpha_cd * norm.get("CD", 0.0)
    )
    S["S_T"] = clamp(S_T)

    S_L = (
        cfg.beta_dlc * norm.get("DLC", 0.0)
        + cfg.beta_lbr * (1.0 - norm.get("LBR", 1.0))
        + cfg.beta_hcs * norm.get("HCS", 0.0)
    )
    S["S_L"] = clamp(S_L)

    S_A = (
        cfg.gamma_ear * norm.get("EAR", 0.0)
        + cfg.gamma_sdi * (1.0 - norm.get("SDI", 0.0))
        + cfg.gamma_pmg * norm.get("PMG", 0.0)
    )
    S["S_A"] = clamp(S_A)

    if applicability.get("multi_agent", False):
        S_M = (
            cfg.delta_ar * norm.get("AR", 0.0)
            + cfg.delta_rrs * norm.get("RRS", 0.0)
            + cfg.delta_ac * norm.get("AC", 0.0)
        )
        S["S_M"] = clamp(S_M)

    if applicability.get("counterfactual", False):
        S_C = (
            cfg.epsw_rc * norm.get("RC", 0.0)
            + cfg.epsw_csi * (1.0 - norm.get("CSI", 1.0))
            + cfg.epsw_ct * norm.get("CT", 0.0)
        )
        S["S_C"] = clamp(S_C)

    return S
