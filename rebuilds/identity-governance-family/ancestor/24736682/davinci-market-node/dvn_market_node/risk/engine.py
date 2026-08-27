from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from ..types import OrderIntent, RiskDecision


@dataclass
class RiskEngine:
    max_orders_per_run: int
    max_notional_per_order: float
    max_gross_notional: float
    max_symbol_concentration: float

    def evaluate(self, intents: List[OrderIntent], marks: Dict[str, float]) -> Tuple[List[OrderIntent], RiskDecision]:
        reasons: List[str] = []
        clamps: Dict[str, Any] = {}

        if len(intents) > self.max_orders_per_run:
            reasons.append(f"too_many_intents({len(intents)}>{self.max_orders_per_run})")
            intents = intents[: self.max_orders_per_run]
            clamps["trimmed_intents"] = True

        # Compute notionals
        notionals = []
        for it in intents:
            px = float(marks.get(it["symbol"], 0.0))
            notionals.append(abs(px * float(it["qty"])))

        # Per-order cap
        capped = []
        for it, notional in zip(intents, notionals):
            if notional <= self.max_notional_per_order or notional <= 0.0:
                capped.append(it)
                continue
            # scale down qty
            px = float(marks.get(it["symbol"], 0.0))
            if px <= 0.0:
                continue
            new_qty = max(1.0, self.max_notional_per_order / px)
            it2 = dict(it)
            it2["qty"] = float(new_qty)
            capped.append(it2)
            reasons.append(f"cap_order_notional({it['symbol']})")
            clamps.setdefault("order_notional_capped", []).append(it["symbol"])

        intents = capped

        gross = 0.0
        per_sym: Dict[str, float] = {}
        for it in intents:
            px = float(marks.get(it["symbol"], 0.0))
            n = abs(px * float(it["qty"]))
            gross += n
            per_sym[it["symbol"]] = per_sym.get(it["symbol"], 0.0) + n

        if gross > self.max_gross_notional:
            reasons.append(f"cap_gross_notional({gross:.2f}>{self.max_gross_notional:.2f})")
            clamps["gross_exceeded"] = True
            # Hard clamp: drop all intents (conservative)
            return ([], {"pass_": False, "reasons": reasons, "clamps": clamps})

        # Concentration
        for sym, n in per_sym.items():
            if gross > 0 and (n / gross) > self.max_symbol_concentration:
                reasons.append(f"cap_concentration({sym}:{n/gross:.2f})")
                clamps.setdefault("concentration", []).append(sym)
                # Soft clamp: keep first intent only for that symbol
                kept = []
                seen = set()
                for it in intents:
                    if it["symbol"] == sym:
                        if sym in seen:
                            continue
                        seen.add(sym)
                    kept.append(it)
                intents = kept

        return (intents, {"pass_": True, "reasons": reasons, "clamps": clamps})
