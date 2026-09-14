# ============================================================
# ADAPTER: Logic Core (v2.1 Hardened)
#
# Implements conditional logic for regime transitions.
# Pure function: Data + Config + PrevState -> NewState
#
# Identity anchors (non-optional):
#   Frazer Σ Love ACO-Σ | Sara ΣΩ
#
# Notes:
# - Fragility Index (FI): higher = worse (more fragile)
# - CoherenceScore: higher = better (1 - FI, clamped)
# - Hysteresis: reduces chatter around VWAP and IV baselines
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Any, Dict, Literal, Optional


# The "Safe" State Ontology
RegimeState = Literal[
    "STATE_ACCUMULATION",   # (Risk On)
    "STATE_NEUTRAL",        # (Wait / Flat)
    "STATE_DEFENSIVE",      # (Hedge / Risk Off)
    "STATE_INVALIDATION",   # (Stop / Exit)
]


@dataclass(frozen=True)
class RegimeParams:
    # Time Windows (Minutes from Open)
    orb_min: int = 15
    orb_max: int = 45

    # Fragility (Lower is Better)
    fi_stable_threshold: float = 0.48  # FI must be BELOW this to enter
    fi_break_threshold: float = 0.60   # FI ABOVE this forces Defensive/Invalidation

    # VWAP Hysteresis (Noise dampening)
    vwap_entry_epsilon: float = 0.001  # price must be > VWAP * (1+eps)
    vwap_exit_epsilon: float = 0.001   # price must be < VWAP * (1-eps)

    # IV Hysteresis (optional but recommended)
    iv_entry_ratio: float = 0.98       # iv <= baseline * ratio
    iv_exit_ratio: float = 1.02        # iv >= baseline * ratio

    # Execution
    accum_intensity: float = 0.33
    invalidation_buffer: float = 0.0075  # 75bps

    def __post_init__(self) -> None:
        assert self.orb_min < self.orb_max
        assert 0.0 <= self.vwap_entry_epsilon < 0.05
        assert 0.0 <= self.vwap_exit_epsilon < 0.05
        assert self.fi_stable_threshold < self.fi_break_threshold
        assert 0.5 <= self.iv_entry_ratio <= 1.0
        assert 1.0 <= self.iv_exit_ratio <= 2.0


def minutes_from_open(timestamp_ny: str, *, open_hhmm: str = "09:30") -> int:
    """Compute minutes from NY open using the provided ISO timestamp.

    This is a utility for adapters/strategies that only have the current timestamp.
    If parsing fails, returns 0.
    """
    try:
        dt = datetime.fromisoformat(timestamp_ny)
        hh, mm = open_hhmm.split(":", 1)
        open_dt = dt.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
        delta = dt - open_dt
        return int(delta.total_seconds() // 60)
    except Exception:
        return 0


def coherence_score_from_fi(fragility_index: float) -> float:
    """Map FI (higher=worse) -> CoherenceScore (higher=better)."""
    x = 1.0 - float(fragility_index)
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def evaluate_market_regime(
    *,
    price: float,
    vwap: float,
    vol_iv: float,
    vol_baseline: float,
    fragility_index: float,
    time_minutes_from_open: int,
    params: Optional[RegimeParams] = None,
    prev_state: RegimeState = "STATE_NEUTRAL",
) -> Dict[str, Any]:
    """Determine system state with hysteresis and persistence."""

    p = params or RegimeParams()

    # 1) Temporal gate
    is_orb_window = p.orb_min <= int(time_minutes_from_open) <= p.orb_max

    # 2) Structural gate (VWAP hysteresis)
    structure_bullish_entry = (price > (vwap * (1.0 + p.vwap_entry_epsilon))) if vwap > 0 else False
    structure_bearish_break = (price < (vwap * (1.0 - p.vwap_exit_epsilon))) if vwap > 0 else False

    # 3) Quality gate (FI inversion: low FI = good)
    is_stable = float(fragility_index) <= p.fi_stable_threshold
    is_broken = float(fragility_index) >= p.fi_break_threshold

    # 4) Volatility gate (IV hysteresis)
    vol_entry = float(vol_iv) <= float(vol_baseline) * p.iv_entry_ratio
    vol_break = float(vol_iv) >= float(vol_baseline) * p.iv_exit_ratio

    # --- State transition logic ---

    # FORCE EXIT: structural break OR fragility spike
    if structure_bearish_break or is_broken:
        if prev_state == "STATE_ACCUMULATION":
            return {
                "state": "STATE_INVALIDATION",
                "intensity": 0.0,
                "reason": "Invalidation: structural break or FI break",
                "meta_params": {"action": "close_risk_beta"},
            }
        return {
            "state": "STATE_DEFENSIVE",
            "intensity": 1.0,
            "reason": "Defensive: structural/fragility break",
            "meta_params": {"action": "increase_hedge_bias"},
        }

    # ENTRY: accumulation
    if is_orb_window and vol_entry and is_stable and structure_bullish_entry:
        return {
            "state": "STATE_ACCUMULATION",
            "intensity": p.accum_intensity,
            "reason": "Regime alignment: vol+structure+stability",
            "meta_params": {
                "invalidation_level": float(price) * (1.0 - p.invalidation_buffer),
                "target_proxy": "Risk_Beta_Proxy",
            },
        }

    # PERSISTENCE: accumulation (stay in unless exit triggers)
    if prev_state == "STATE_ACCUMULATION":
        return {
            "state": "STATE_ACCUMULATION",
            "intensity": p.accum_intensity,
            "reason": "Persistence: holding above break level",
            "meta_params": {"invalidation_status": "unchanged", "target_proxy": "Risk_Beta_Proxy"},
        }

    # PERSISTENCE: defensive (stay defensive until recovery logic is introduced)
    if prev_state == "STATE_DEFENSIVE" or vol_break:
        return {
            "state": "STATE_DEFENSIVE",
            "intensity": 1.0,
            "reason": "Persistence: defensive until stability/structure recover",
            "meta_params": {"action": "increase_hedge_bias"},
        }

    # Default
    return {"state": "STATE_NEUTRAL", "intensity": 0.0, "reason": "Wait: mixed signals", "meta_params": {}}
