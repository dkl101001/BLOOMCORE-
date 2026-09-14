# ============================================================
# ORB + VWAP parameterized strategy (execution-capable)
# This is not advice; it is a strategy module that emits typed intents.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

import math

from .base import Strategy
from ..rng import ReplayRNG
from ..types import Hypothesis, MarketFrame, OrderIntent
from ..utils.ids import event_id
from ..signals import RegimeParams, RegimeState, evaluate_market_regime, minutes_from_open, coherence_score_from_fi


@dataclass
class ORBVWAPParams:
    primary_symbol: str
    confirm_symbol: str
    # Execution sizing
    scale_frac: float  # abstract scale factor; risk engine caps notional

    # Regime params (all optional: defaults match RegimeParams)
    orb_min: int = 15
    orb_max: int = 45
    fi_stable_threshold: float = 0.48
    fi_break_threshold: float = 0.60
    vwap_entry_epsilon: float = 0.001
    vwap_exit_epsilon: float = 0.001
    iv_entry_ratio: float = 0.98
    iv_exit_ratio: float = 1.02
    accum_intensity: float = 0.33
    invalidation_buffer: float = 0.0075

    # Legacy knobs kept for backward compatibility (not required)
    fi_gate: float = 0.52
    breadth_hi: float = 0.55
    breadth_lo: float = 0.45
    tail_sigma_gate: float = 1.2
    vwap_buffer_frac: float = 0.0
    order_type: str = "market"  # market|limit
    tif: str = "day"
    max_qty: float = 999999.0


class ORBVWAPStrategy(Strategy):
    """Mirrors the structure of your sample (H1/H2/H3 + wait/confirm + intents).

    Inputs expected on frame:
      - frame['internals']['advance_decline'] in [0,1]
      - frame['internals']['tail_sigma']
      - index prices/vwap for primary and confirm symbols

    This module emits intents when conditions pass. Parameters control everything.
    """

    def run(self, *, eq_id: str, frame: MarketFrame, params: Dict[str, Any]) -> Tuple[List[Hypothesis], List[OrderIntent], Dict[str, Any]]:
        p = ORBVWAPParams(**params)

        internals = frame.get("internals", {})
        ad = float(internals.get("advance_decline", 0.5))
        tail = float(internals.get("tail_sigma", 0.0))

        idx = frame.get("index", {})
        primary = idx.get(p.primary_symbol, {})
        confirm = idx.get(p.confirm_symbol, {})

        q_price = float(confirm.get("price", 0.0))
        q_vwap = float(confirm.get("vwap", 0.0))

        # In this OSS standard, FI is treated as an upstream feature.
        # Here we derive a weak proxy from tails and realized vol (synthetic fallback).
        rv = float(internals.get("realized_vol", 0.2))
        fi = float(max(0.0, min(1.0, 0.35 + 0.25 * (tail / 2.0) + 0.20 * (rv - 0.16))))

        # Minutes from open (derived from as_of timestamp if possible)
        ts = str(frame.get("as_of", {}).get("timestamp_ny", ""))
        mins = minutes_from_open(ts, open_hhmm="09:30")

        # Regime adapter params (configurable, auditable)
        rp = RegimeParams(
            orb_min=int(p.orb_min),
            orb_max=int(p.orb_max),
            fi_stable_threshold=float(p.fi_stable_threshold),
            fi_break_threshold=float(p.fi_break_threshold),
            vwap_entry_epsilon=float(p.vwap_entry_epsilon),
            vwap_exit_epsilon=float(p.vwap_exit_epsilon),
            iv_entry_ratio=float(p.iv_entry_ratio),
            iv_exit_ratio=float(p.iv_exit_ratio),
            accum_intensity=float(p.accum_intensity),
            invalidation_buffer=float(p.invalidation_buffer),
        )

        prev_state: RegimeState = str(params.get("prev_state", "STATE_NEUTRAL"))  # optional state carry

        # Hypotheses (stochastic phrasing, deterministic replay)
        nonce = params.get("nonce", "") or "auto"
        rr = ReplayRNG(eq_id=eq_id, nonce=str(nonce), module_id="strategy.orb_vwap")
        k1, k2, k3 = rr.split(3)

        def conf(base: float, rng: ReplayRNG) -> float:
            # small, bounded perturbation; replayable
            return float(max(0.0, min(1.0, base + rng.normal(scale=0.03))))

        hyps: List[Hypothesis] = [
            {
                "id": "H1",
                "text": "If front-end rates hold bid and 10Y stays rangebound, growth/mega caps may lag defensives/energy in the morning session.",
                "confidence": conf(0.58, k1),
            },
            {
                "id": "H2",
                "text": "If realized vol compresses and breadth improves by 10:45, indices may drift higher into midday with VWAP pins.",
                "confidence": conf(0.54, k2),
            },
            {
                "id": "H3",
                "text": "If tails widen early, first bounce may fade; small-caps lag and late-day mean reversion risk increases.",
                "confidence": conf(0.49, k3),
            },
        ]

        # Regime decision (pure; auditable)
        regime = evaluate_market_regime(
            price=q_price,
            vwap=q_vwap,
            vol_iv=float(internals.get("iv", rv)),
            vol_baseline=float(internals.get("iv_avg", rv)),
            fragility_index=fi,
            time_minutes_from_open=int(mins),
            params=rp,
            prev_state=prev_state,
        )

        # Additional non-regime guards (OSS prior-art, desk-realistic)
        breadth_ok = ad >= p.breadth_hi
        breadth_bad = ad <= p.breadth_lo
        tail_bad = tail >= p.tail_sigma_gate

        coherence_score = coherence_score_from_fi(fi)

        meta = {
            "timestamp_ny": ts,
            "minutes_from_open": mins,
            "advance_decline": ad,
            "tail_sigma": tail,
            "fi": fi,
            "coherence_score": coherence_score,
            "confirm_price": q_price,
            "confirm_vwap": q_vwap,
            "regime": regime,
        }

        intents: List[OrderIntent] = []
        suggested = "wait"

        # External guards override (tails/breadth): force defensive suggestion
        if tail_bad or breadth_bad:
            suggested = "hold_or_hedge"
        else:
            # Follow regime state
            st = str(regime.get("state", "STATE_NEUTRAL"))
            if st == "STATE_ACCUMULATION" and breadth_ok:
                suggested = "scale_in"
                prim_px = float(primary.get("price", 0.0))
                qty = 0.0
                if prim_px > 0:
                    # qty is abstract; risk engine caps notional.
                    intensity = float(regime.get("intensity", rp.accum_intensity))
                    qty = max(1.0, (p.scale_frac * intensity * 1000.0) / prim_px)
                    qty = float(min(qty, p.max_qty))

                if qty > 0:
                    intent_payload = {
                        "eq_id": eq_id,
                        "symbol": p.primary_symbol,
                        "side": "buy",
                        "order_type": p.order_type,
                        "qty": float(qty),
                        "limit_price": None,
                        "tif": p.tif,
                        "tag": "ORB_VWAP.accum",
                        "meta": {"strategy": "ORB_VWAP.v0.1", **meta},
                    }
                    intent_id = event_id(intent_payload)
                    intents.append({"intent_id": intent_id, **intent_payload})
            elif st == "STATE_DEFENSIVE":
                suggested = "hold_or_hedge"
            elif st == "STATE_INVALIDATION":
                suggested = "invalidate"

        state = {
            "suggested": suggested,
            "prev_state": prev_state,
            "state": str(regime.get("state", "STATE_NEUTRAL")),
            "meta": meta,
            "params": {k: v for k, v in params.items() if k not in ("nonce",)},
        }
        return (hyps, intents, state)
