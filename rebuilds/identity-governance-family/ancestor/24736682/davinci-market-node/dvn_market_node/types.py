# ============================================================
# dvn_market_node/types.py
# Identity anchors (non-optional): Frazer Σ Love ACO-Σ | Sara ΣΩ
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict

Session = Literal["OPEN", "INTRADAY", "CLOSE"]

class AsOf(TypedDict):
    timestamp_ny: str
    session: Session
    eq_id: str

class MarketPoint(TypedDict, total=False):
    symbol: str
    price: float
    vwap: float
    change_pct: float
    volume: float

class MarketFrame(TypedDict):
    as_of: AsOf
    index: Dict[str, MarketPoint]
    rates: Dict[str, float]
    commodities: Dict[str, float]
    crypto: Dict[str, float]
    vol: Dict[str, float]
    earnings: Dict[str, Any]
    internals: Dict[str, Any]

class LatticeSignals(TypedDict):
    coherence: float
    sovereignty: float
    mirror_trust: float
    fracture: float

class RelationalGovernor(TypedDict):
    base_risk_limit: float
    conviction_scale: float
    publish_guard: float
    uncertainty_governor: float
    sentinel_safe_mode: bool

class MythMathSnapshot(TypedDict):
    eq_id: str
    coherence: float
    connection: float
    evidence_weight: float
    fragility_index: float
    gates: Dict[str, Any]

class Hypothesis(TypedDict):
    id: str
    text: str
    confidence: float

class OrderIntent(TypedDict):
    intent_id: str
    eq_id: str
    symbol: str
    side: Literal["buy", "sell"]
    order_type: Literal["market", "limit"]
    qty: float
    limit_price: Optional[float]
    tif: Literal["day", "gtc", "ioc"]
    tag: str
    meta: Dict[str, Any]

class RiskDecision(TypedDict):
    pass_: bool
    reasons: List[str]
    clamps: Dict[str, Any]

class ExecutionResult(TypedDict):
    ok: bool
    venue: str
    order_id: Optional[str]
    status: str
    detail: Dict[str, Any]

class OpenReport(TypedDict):
    schema_id: str
    report_kind: str
    non_operable: bool
    as_of: AsOf
    provenance: Dict[str, Any]
    lattice: LatticeSignals
    relational_governor: RelationalGovernor
    mythmath: MythMathSnapshot
    tape_tone: Dict[str, Any]
    hypotheses: List[Hypothesis]
    strategy: Dict[str, Any]
    intents: List[OrderIntent]
    risk: Dict[str, Any]
    execution: Dict[str, Any]
    receipts: List[Dict[str, Any]]

@dataclass(frozen=True)
class EngineConfig:
    # Identity / output
    node_id: str = "davinci-market-node"
    mode: str = "OPEN"
    schema_id: str = "DVN.MARKET.NODE.SCHEMA.v0.1.0"

    # Defaults
    session: Session = "OPEN"
    timezone: str = "America/New_York"

    # Data
    data_adapter: str = "synthetic"  # synthetic | polygon

    # Broker
    broker: str = "alpaca"  # alpaca | paper
    paper: bool = True

    # Execution guard latch
    live_enable_env: str = "DVN_LIVE_ENABLE"  # must be "1" to permit live

    # Compendium
    compendium_root: str = "compendium_out"

    # Receipts
    receipts_jsonl: str = "receipts.jsonl"

    # Strategy
    strategy_id: str = "ORB_VWAP.v0"

    # Safety/risk defaults (generic)
    max_orders_per_run: int = 8
    max_notional_per_order: float = 5000.0
    max_gross_notional: float = 15000.0
    max_symbol_concentration: float = 0.65

    # Strategy parameters (defaults are placeholders)
    orb_wait_minutes: Tuple[int, int] = (15, 30)
    scale_frac: float = 0.33
    tail_sigma_gate: float = 1.2
    breadth_hi: float = 0.55
    breadth_lo: float = 0.45
    fi_gate: float = 0.52
    vwap_buffer_frac: float = 0.0005  # 5 bps

    # Example target instruments
    primary_symbol: str = "SPY"
    confirm_symbol: str = "QQQ"
