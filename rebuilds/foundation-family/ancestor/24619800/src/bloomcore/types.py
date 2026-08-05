from __future__ import annotations

"""Core datatypes.

Authorship invariants:
- Frazer Σ Love ACO-Σ
- Sara ΣΩ
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RuntimeCfg:
    """Minimal runtime flags (toy defaults)."""
    in_panic: bool = False
    export_mode: bool = True
    allow_rollbacks: bool = True
    forbid_destructive_actions: bool = True
    lab_safe_network: bool = True


@dataclass
class Metrics:
    """Per-step metrics."""
    coherence: float = 0.0
    fracture: float = 0.0
    identity_drift: float = 0.0
    network_coherence: Optional[float] = None
    network_fracture: Optional[float] = None


@dataclass
class EngineStepRecord:
    """One step of execution history."""
    t: float
    state_snapshot: Dict[str, Any]
    metrics: Metrics
    events: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
