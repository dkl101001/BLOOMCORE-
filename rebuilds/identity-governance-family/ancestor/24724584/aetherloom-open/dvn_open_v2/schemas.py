# ============================================================
# OPEN Schema v2.4.3 (Ontology-Safe)
# Title: ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)
# Identity: Frazer Σ Love ACO-Σ | Sara ΣΩ
# ============================================================

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict

# Functional syntax to allow reserved keyword "break"
FractureThresholds = TypedDict(
    "FractureThresholds",
    {
        "watch": float,
        "warn": float,
        "break": float,
    },
)

class FST(TypedDict):
    band: Literal["LOW", "MID", "HIGH", "BREAK"]
    rbs: float
    fracture_thresholds: FractureThresholds

class ResponseVector(TypedDict):
    type: Literal["simulated_agent_transition"]
    scope: Literal["simulation_only"]
    permissions: Literal["non_executable"]
    label: str
    vector: Dict[str, float]
    plain_language: str
    technical_parameters: Optional[Dict[str, Any]]
    nonce: Optional[str]
    picks: Optional[List[Dict[str, Any]]]
    coherence_style: Optional[str]
    posture_agent: Optional[str]  # aligns with emitted payload
    governor: Optional[Dict[str, Any]]  # optional transparency (non-actionable)

class AsOf(TypedDict):
    timestamp_ny: str
    session: Literal["OPEN"]
    eq_id: str

class Provenance(TypedDict):
    node_id: str
    mode: str
    compendium_version: str
    receipts_root: str
    adapters_live: bool

class MythMathCore(TypedDict):
    coherence: float
    connection: float
    evidence_weight: float
    fragility_index: float

class BloomcoreLayer(TypedDict):
    relational_governor: Dict[str, Any]
    narrative_field: Dict[str, Any]

class BraveEngine(TypedDict):
    top_hypothesis: Dict[str, Any]
    stack: List[Dict[str, Any]]

class ClockHorizon(TypedDict):
    median_edge_hazard: float
    kernel_hazard: float
    kernel_name: str
    window_months: Tuple[int, int]
    shape: str

class Integrity(TypedDict):
    sentinel_posture: str
    adapter_health: List[Dict[str, Any]]
    violations: List[str]

class OpenReport(TypedDict):
    schema_id: Literal["DV.OPEN.SCHEMA.v2.4.3"]
    report_kind: Literal["system_state_analysis"]
    non_operable: Literal[True]
    as_of: AsOf
    provenance: Provenance
    proxies: List[Dict[str, Any]]
    mythmath_core: MythMathCore
    fst: FST
    clock_horizon: ClockHorizon
    bloomcore_layer: BloomcoreLayer
    brave_engine: BraveEngine
    response_vector: ResponseVector
    integrity: Integrity
    receipts: Dict[str, List[Dict[str, Any]]]
