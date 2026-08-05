from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol
import random


@dataclass(frozen=True)
class BloomforceParams:
    """Public parameters only."""
    dtau_gain: float = 1.0
    grad_rho_gain: float = 1.0
    max_force_norm: float = 1e6
    receipt_schema: str = "BLOOMFORCE.CORE.v1"


@dataclass
class BloomforceState:
    """Minimal state, intentionally generic."""
    tick: int = 0
    x: float = 0.0
    last_force: float = 0.0
    rng_state: Optional[tuple] = None


@dataclass(frozen=True)
class ObsBundle:
    """Public observation bundle contract."""
    psi_rho: float
    grad_rho: float
    delta_tau_mass: float


class GateProvider(Protocol):
    def __call__(self, *, state: BloomforceState, obs: ObsBundle, rng: random.Random) -> float: ...


class ObsProvider(Protocol):
    def __call__(self, *, state: BloomforceState, raw: Dict[str, Any], rng: random.Random) -> ObsBundle: ...
