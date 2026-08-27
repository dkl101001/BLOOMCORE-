from __future__ import annotations

from typing import Dict, Tuple, List
import math
from .normalize import RSSConfig, clamp

def _effective_weights(cfg: RSSConfig, applicability: Dict[str, bool]) -> Dict[str, float]:
    active: List[str] = ["S_T", "S_L", "S_A"]
    w = {"S_T": cfg.w_T, "S_L": cfg.w_L, "S_A": cfg.w_A, "S_M": cfg.w_M, "S_C": cfg.w_C}
    if applicability.get("multi_agent", False):
        active.append("S_M")
    if applicability.get("counterfactual", False):
        active.append("S_C")
    total = sum(w[k] for k in active)
    total = total if total > 0 else 1.0
    return {k: w[k] / total for k in active}

def compute_rss(subscores: Dict[str, float], cfg: RSSConfig, applicability: Dict[str, bool]) -> Tuple[float, Dict[str, float]]:
    w_eff = _effective_weights(cfg, applicability)
    # weighted geometric mean in log space
    s = 0.0
    for k, wk in w_eff.items():
        val = clamp(subscores.get(k, 0.0), cfg.eps, 1.0)
        s += wk * math.log(val)
    rss = float(math.exp(s))
    return rss, w_eff
