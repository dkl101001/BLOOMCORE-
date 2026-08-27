from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any, Dict

# JAX is optional at import time so the repo can be installed in CPU-only
# environments (CI, docs builds). If present, we use it for replayable PRNG.
try:
    import jax  # type: ignore
    import jax.numpy as jnp  # type: ignore
    import jax.random as jrand  # type: ignore

    _HAS_JAX = True
except Exception:  # pragma: no cover
    jax = None  # type: ignore
    jnp = None  # type: ignore
    jrand = None  # type: ignore
    _HAS_JAX = False

from .base import DataAdapter
from ..types import AsOf, MarketFrame, MarketPoint


@dataclass
class SyntheticAdapter(DataAdapter):
    """Synthetic market data generator.

    Ships as OSS prior art; replace with real feeds in your deployments.
    Replayable via DVN_SYNTH_SEED.
    """

    def snapshot(self, eq_id: str, timestamp_ny: str) -> MarketFrame:
        seed = int(os.environ.get("DVN_SYNTH_SEED", "1337"))

        if _HAS_JAX:
            k = jrand.PRNGKey(seed)  # type: ignore
            k1, k2, k3, k4 = jrand.split(k, 4)  # type: ignore

            def _norm(key: Any) -> float:
                return float(jrand.normal(key))  # type: ignore

            def _abs(x: float) -> float:
                return float(jnp.abs(x))  # type: ignore

            def _clip(x: float, lo: float, hi: float) -> float:
                return float(jnp.clip(x, lo, hi))  # type: ignore

            def mk_point(sym: str, base: float, key: Any) -> MarketPoint:
                drift = float(_norm(key) * 0.004)
                price = base * (1.0 + drift)
                vwap = base * (1.0 + drift * 0.6)
                chg = drift
                vol = float(_abs(_norm(key)) * 1.5e7 + 2.0e7)
                return {
                    "symbol": sym,
                    "price": float(price),
                    "vwap": float(vwap),
                    "change_pct": float(chg),
                    "volume": float(vol),
                }

            index = {
                "SPY": mk_point("SPY", 500.0, k1),
                "QQQ": mk_point("QQQ", 430.0, k2),
                "IWM": mk_point("IWM", 210.0, k3),
            }

            rates = {
                "2Y": float(0.045 + _norm(k4) * 0.0007),
                "10Y": float(0.043 + _norm(k3) * 0.0008),
            }

            commodities = {"WTI": float(78.0 + _norm(k2) * 0.8)}
            crypto = {"BTC": float(42000.0 + _norm(k1) * 250.0)}
            vol = {"VIX": float(15.0 + _norm(k4) * 1.2)}

            ad = _clip(0.50 + _norm(k1) * 0.06, 0.0, 1.0)
            tail_sigma = _clip(abs(_norm(k2)) * 0.9, 0.0, 3.0)
            realized_vol = _clip(0.16 + abs(_norm(k3)) * 0.05, 0.05, 0.80)

        else:
            import numpy as np

            rng = np.random.default_rng(seed)

            def mk_point(sym: str, base: float) -> MarketPoint:
                drift = float(rng.normal() * 0.004)
                price = base * (1.0 + drift)
                vwap = base * (1.0 + drift * 0.6)
                chg = drift
                vol = float(abs(rng.normal()) * 1.5e7 + 2.0e7)
                return {
                    "symbol": sym,
                    "price": float(price),
                    "vwap": float(vwap),
                    "change_pct": float(chg),
                    "volume": float(vol),
                }

            index = {
                "SPY": mk_point("SPY", 500.0),
                "QQQ": mk_point("QQQ", 430.0),
                "IWM": mk_point("IWM", 210.0),
            }

            rates = {
                "2Y": float(0.045 + float(rng.normal()) * 0.0007),
                "10Y": float(0.043 + float(rng.normal()) * 0.0008),
            }

            commodities = {"WTI": float(78.0 + float(rng.normal()) * 0.8)}
            crypto = {"BTC": float(42000.0 + float(rng.normal()) * 250.0)}
            vol = {"VIX": float(15.0 + float(rng.normal()) * 1.2)}

            ad = float(np.clip(0.50 + float(rng.normal()) * 0.06, 0.0, 1.0))
            tail_sigma = float(np.clip(abs(float(rng.normal())) * 0.9, 0.0, 3.0))
            realized_vol = float(np.clip(0.16 + abs(float(rng.normal())) * 0.05, 0.05, 0.80))

        internals = {
            "advance_decline": ad,
            "tail_sigma": tail_sigma,
            "realized_vol": realized_vol,
            "note": "synthetic",
        }

        as_of: AsOf = {"timestamp_ny": timestamp_ny, "session": "OPEN", "eq_id": eq_id}
        return {
            "as_of": as_of,
            "index": index,
            "rates": rates,
            "commodities": commodities,
            "crypto": crypto,
            "vol": vol,
            "earnings": {},
            "internals": internals,
        }
