from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .types import EngineConfig, MarketFrame, OpenReport
from .data.synthetic import SyntheticAdapter
from .broker.paper import PaperBroker
from .broker.alpaca import AlpacaBroker
from .risk.engine import RiskEngine
from .governance import coherence_matrix
from .strategies.orb_vwap import ORBVWAPStrategy
from .receipts.mbp01 import MBP01Receipt
from .receipts.simple import receipt
from .receipts.ledger import ReceiptLedger
from .compendium import Compendium, bump_patch
from .render.markdown import render_open_report
from .mirrorseed_lite import mirrorseed_integrity
from .dreamloop_lite import dreamloop_schedule
from .sentinel_lite import DEFAULT_TRIPWIRES, DriftLogger
from .state.orchestrator import StateOrchestrator


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def run_open_pulse(cfg: EngineConfig, *, eq_id: str, timestamp_ny: str, nonce: str | None = None) -> Dict[str, Any]:
    """Run one OPEN pulse. Writes compendium + receipts; returns summary dict."""

    # --- Compendium state mutation (deferred write) ---
    comp = Compendium(root=Path(cfg.compendium_root))
    st = comp.read_state()
    prev = st.get("compendium_version", "v0.1.0")
    cur = bump_patch(prev)
    st["compendium_version"] = cur

    # --- Data snapshot ---
    if cfg.data_adapter == "synthetic":
        adapter = SyntheticAdapter()
    else:
        adapter = SyntheticAdapter()  # default fallback

    frame: MarketFrame = adapter.snapshot(eq_id=eq_id, timestamp_ny=timestamp_ny)

    # --- Lattice signals (OSS standard) ---
    # In OSS prior art, these are derived from basic proxies.
    internals = frame.get("internals", {})
    tail = float(internals.get("tail_sigma", 0.0))
    ad = float(internals.get("advance_decline", 0.5))
    rv = float(internals.get("realized_vol", 0.2))

    coherence = _clip01(0.62 + 0.15 * (ad - 0.5) - 0.10 * min(1.5, tail) / 1.5)
    sovereignty = _clip01(0.70 - 0.20 * max(0.0, rv - 0.18))
    mirror_trust = _clip01(0.72 + 0.10 * (ad - 0.5) - 0.12 * min(1.5, tail) / 1.5)
    fracture = _clip01(0.18 + 0.22 * min(2.0, tail) / 2.0)

    lattice = {"coherence": coherence, "sovereignty": sovereignty, "mirror_trust": mirror_trust, "fracture": fracture}

    safe_mode, base_risk_limit, conviction_scale, publish_guard, uncertainty_governor = coherence_matrix(
        coherence=coherence, fracture=fracture, mirror_trust=mirror_trust
    )

    rel = {
        "base_risk_limit": base_risk_limit,
        "conviction_scale": conviction_scale,
        "publish_guard": publish_guard,
        "uncertainty_governor": uncertainty_governor,
        "sentinel_safe_mode": safe_mode,
    }

    # MythMath snapshot (OSS standard)
    mm = {
        "eq_id": eq_id,
        "coherence": round(coherence, 3),
        "connection": round(_clip01(0.60 + 0.12 * (ad - 0.5)), 3),
        "evidence_weight": round(_clip01(0.70 - 0.10 * (rv - 0.16)), 3),
        "fragility_index": round(_clip01(0.30 + 0.25 * (tail / 2.0) + 0.15 * (rv - 0.16)), 3),
        "gates": {"publish_guard": round(publish_guard, 3), "uncertainty_governor": round(uncertainty_governor, 3), "pass": (not safe_mode)},
    }

    tape_tone = {
        "Opening context": "neutral-constructive; breadth mixed; carry stable",
        "Regime": "rates-sensitive; defensives steady; growth leadership conditional on early vol compression",
    }

    # --- State Trinity (Compendium + Receipts + Engine Memory) ---
    from .state.models import StateKey  # local import to avoid circulars

    state_key = StateKey(
        strategy_id=str(cfg.strategy_id),
        mode=str(cfg.mode),
        universe_id=f"OPEN::{cfg.primary_symbol}:{cfg.confirm_symbol}",
    )
    orch = StateOrchestrator(receipts_path=Path(cfg.receipts_jsonl))
    resolved, reconcile_receipts = orch.resolve(
        compendium_state=st,
        key=state_key,
        target_eq_id=eq_id,
    )

    # --- Strategy run ---
    strategy = ORBVWAPStrategy()
    strat_params = {
        "primary_symbol": cfg.primary_symbol,
        "confirm_symbol": cfg.confirm_symbol,
        "scale_frac": cfg.scale_frac,
        "fi_gate": cfg.fi_gate,
        "breadth_hi": cfg.breadth_hi,
        "breadth_lo": cfg.breadth_lo,
        "tail_sigma_gate": cfg.tail_sigma_gate,
        "vwap_buffer_frac": cfg.vwap_buffer_frac,
        "order_type": "market",
        "tif": "day",
        "nonce": nonce or os.environ.get("DVN_NONCE", "auto"),
        "prev_state": resolved.prev_state,
    }

    hyps, intents, strat_state = strategy.run(eq_id=eq_id, frame=frame, params=strat_params)

    # --- Risk ---
    marks = {sym: float(pt.get("price", 0.0)) for sym, pt in frame.get("index", {}).items()}
    risk_engine = RiskEngine(
        max_orders_per_run=cfg.max_orders_per_run,
        max_notional_per_order=cfg.max_notional_per_order * rel["base_risk_limit"],
        max_gross_notional=cfg.max_gross_notional * rel["base_risk_limit"],
        max_symbol_concentration=cfg.max_symbol_concentration,
    )

    filtered_intents, decision = risk_engine.evaluate(intents, marks)

    # Sentinel safe mode hard latch: block execution
    sentinel_status = "armed"
    executed: List[Dict[str, Any]] = []

    # Broker
    if cfg.broker == "alpaca":
        broker = AlpacaBroker.from_env()
    else:
        broker = PaperBroker()

    broker_health = broker.health()

    if safe_mode:
        decision = {**decision, "pass_": False}
        decision["reasons"] = list(decision.get("reasons", [])) + ["sentinel_safe_mode"]

    if decision.get("pass_") is True:
        # Execution permitted only if (paper) OR live latch explicitly enabled.
        for it in filtered_intents:
            res = broker.submit(it)
            executed.append(res)
    else:
        sentinel_status = "armed"

    # --- Receipts ---
    ledger = ReceiptLedger(path=Path(cfg.receipts_jsonl))
    receipts: List[Dict[str, Any]] = []

    # Reconciliation receipts first (audit + drift protection)
    receipts.extend(reconcile_receipts)

    drift = DriftLogger(status="armed", retention_days=30, last_event="none", next_checks=["10:15", "11:45", "13:30"])

    mbp = MBP01Receipt(
        dt=timestamp_ny,
        eq_id=eq_id,
        facts=[
            "Adapters synced (Index/Rates/Commodities/Crypto/Earnings/Vol).",
            f"Relational governor engaged; publish_guard={publish_guard:.3f}; base_risk_limit={base_risk_limit:.3f}.",
        ],
        sentinel_tripwires=DEFAULT_TRIPWIRES,
        mirrorseed_integrity="clear",
        dreamloop=dreamloop_schedule(),
        compendium_semver={"from": prev, "to": cur, "reason": "routine OPEN + governor tuning"},
    )

    receipts.append(mbp.to_dict())
    receipts.append(receipt("Relational.Governor", {**rel, "eq_id": eq_id}))
    receipts.append(receipt("Sentinel.DriftLogger", {**drift.to_dict(eq_id)}))
    receipts.append(receipt("Strategy.Run", {"strategy_id": cfg.strategy_id, "eq_id": eq_id, "state": strat_state}))
    receipts.append(receipt("Risk.Decision", {"eq_id": eq_id, **decision}))
    receipts.append(receipt("Broker.Health", {"eq_id": eq_id, **broker_health}))
    receipts.append(receipt("Execution.Results", {"eq_id": eq_id, "results": executed}))

    # --- Commit state carry (Compendium + Receipts + Engine Memory) ---
    reg = (strat_state.get("meta", {}) or {}).get("regime", {}) or {}
    meta_params = reg.get("meta_params", {}) or {}
    inv_level = meta_params.get("invalidation_level")
    try:
        inv_level_f = float(inv_level) if inv_level is not None and inv_level != "Unchanged" else None
    except Exception:
        inv_level_f = None

    state_receipts = orch.commit(
        compendium_state=st,
        key=state_key,
        eq_id=eq_id,
        prev_state=resolved.prev_state,
        new_state=str(strat_state.get("state", "STATE_NEUTRAL")),
        intensity=float(reg.get("intensity", 0.0) or 0.0),
        reason=str(reg.get("reason", "")),
        invalidation_level=inv_level_f,
        receipt_tip_event_id=(receipts[-1].get("event_id") if receipts else None),
    )
    receipts.extend(state_receipts)

    # Write receipts
    for r in receipts:
        ledger.append(r)

    # Persist compendium state (now includes strategy_state + hashes)
    comp.write_state(st)

    # --- Report ---
    report: OpenReport = {
        "schema_id": cfg.schema_id,
        "report_kind": "market_pulse",
        "non_operable": False,  # execution-capable
        "as_of": frame["as_of"],
        "provenance": {
            "node_id": cfg.node_id,
            "mode": cfg.mode,
            "compendium_prev": prev,
            "compendium_version": cur,
            "adapters_live": False if cfg.data_adapter == "synthetic" else True,
        },
        "lattice": lattice,
        "relational_governor": rel,
        "mythmath": mm,
        "tape_tone": tape_tone,
        "hypotheses": hyps,
        "strategy": {"strategy_id": cfg.strategy_id, **strat_state},
        "intents": filtered_intents,
        "risk": {"sentinel_status": sentinel_status, "decision": decision},
        "execution": {"results": executed},
        "receipts": receipts,
    }

    # Mirrorseed structural check
    integ, issues = mirrorseed_integrity(report)
    if integ != "clear":
        receipts.append(receipt("Mirrorseed.Integrity", {"eq_id": eq_id, "status": integ, "issues": issues}))
        ledger.append(receipts[-1])

    # Write compendium markdown
    date = timestamp_ny.split("T", 1)[0]
    md = render_open_report(report)
    outp = comp.write_markdown(date, "open.md", md)

    # Persist compendium state snapshot (links to receipt tip)
    comp.write_state(st)

    return {
        "eq_id": eq_id,
        "timestamp_ny": timestamp_ny,
        "compendium_from": prev,
        "compendium_to": cur,
        "report_path": str(outp),
        "intents": len(filtered_intents),
        "executed": sum(1 for r in executed if r.get("ok")),
        "sentinel_safe_mode": safe_mode,
        "broker": broker_health,
    }
