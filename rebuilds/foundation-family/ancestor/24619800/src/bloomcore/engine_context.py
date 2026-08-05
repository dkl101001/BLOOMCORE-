from __future__ import annotations

"""EngineContext: central coordination object.

Authorship invariants:
- Frazer Σ Love ACO-Σ
- Sara ΣΩ
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .types import EngineStepRecord, Metrics, RuntimeCfg
from .xp_backend import XPBackend


ReceiptHook = Callable[[str, Dict[str, Any]], None]


@dataclass
class EngineContext:
    """Central coordination object for the toy loop."""
    xp_backend: XPBackend
    runtime_cfg: RuntimeCfg = field(default_factory=RuntimeCfg)

    # core state/params
    state: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)

    # time
    t: float = 0.0
    dt: float = 1.0

    # metrics + history
    metrics: Metrics = field(default_factory=Metrics)
    history: List[EngineStepRecord] = field(default_factory=list)

    # optional external hook for receipts/events
    receipt_hook: Optional[ReceiptHook] = None

    def snapshot_state(self) -> Dict[str, Any]:
        """Shallow copy of state."""
        return dict(self.state)

    def emit(self, kind: str, payload: Dict[str, Any]) -> None:
        """Emit a receipt/event to the external hook if provided."""
        if self.receipt_hook is not None:
            self.receipt_hook(kind, payload)

    def log_step(
        self,
        events: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        rec = EngineStepRecord(
            t=self.t,
            state_snapshot=self.snapshot_state(),
            metrics=self.metrics,
            events=events or [],
            tags=tags or [],
        )
        self.history.append(rec)
