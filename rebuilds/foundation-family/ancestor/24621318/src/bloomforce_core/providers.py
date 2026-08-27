from __future__ import annotations

from typing import Any, Dict
import random
from .types import BloomforceState, ObsBundle


def default_gate_provider(*, state: BloomforceState, obs: ObsBundle, rng: random.Random) -> float:
    return 1.0


def default_obs_provider(*, state: BloomforceState, raw: Dict[str, Any], rng: random.Random) -> ObsBundle:
    return ObsBundle(
        psi_rho=float(raw.get("psi_rho", 0.0)),
        grad_rho=float(raw.get("grad_rho", 0.0)),
        delta_tau_mass=float(raw.get("delta_tau_mass", 0.0)),
    )
