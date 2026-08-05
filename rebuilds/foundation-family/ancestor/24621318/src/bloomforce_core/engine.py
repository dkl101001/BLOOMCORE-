from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import math, random

from .types import BloomforceParams, BloomforceState, ObsBundle, GateProvider, ObsProvider
from .providers import default_gate_provider, default_obs_provider
from .utils import clamp01
from .ledger import Ledger, Receipt


def compute_bloomforce(params: BloomforceParams, obs: ObsBundle) -> float:
    f = params.grad_rho_gain * float(obs.grad_rho) + params.dtau_gain * float(obs.delta_tau_mass)
    m = float(params.max_force_norm)
    return math.copysign(min(abs(f), m), f)


def apply_force_to_state(state: BloomforceState, *, force_eff: float) -> BloomforceState:
    state.x = float(state.x) + float(force_eff)
    state.last_force = float(force_eff)
    return state


@dataclass
class Engine:
    params: BloomforceParams = field(default_factory=BloomforceParams)
    ledger: Ledger = field(default_factory=Ledger)
    state: BloomforceState = field(default_factory=BloomforceState)

    gate_provider: GateProvider = default_gate_provider
    obs_provider: ObsProvider = default_obs_provider

    capture_rng: bool = True

    def emit(self, kind: str, payload: Dict[str, Any]) -> Receipt:
        return self.ledger.append(kind, payload)

    def step(
        self,
        *,
        raw_obs: Optional[Dict[str, Any]] = None,
        obs: Optional[ObsBundle] = None,
        seed: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Tuple[BloomforceState, Receipt]:
        if meta is None:
            meta = {}

        if self.state.rng_state is not None:
            random.setstate(self.state.rng_state)

        rng = random.Random()
        if seed is not None:
            rng.seed(int(seed))
        else:
            rng.setstate(random.getstate())

        if obs is None:
            obs = self.obs_provider(state=self.state, raw=raw_obs or {}, rng=rng)

        gate = clamp01(self.gate_provider(state=self.state, obs=obs, rng=rng))
        f_bloom = compute_bloomforce(self.params, obs)
        f_eff = float(gate) * float(f_bloom)

        self.state = apply_force_to_state(self.state, force_eff=f_eff)

        if self.capture_rng:
            rs = random.getstate()
            self.state.rng_state = rs
            self.emit("RNG_SNAPSHOT", {"rng_state": list(rs)})

        payload = {
            "schema": self.params.receipt_schema,
            "tick": self.state.tick,
            "obs": {"psi_rho": obs.psi_rho, "grad_rho": obs.grad_rho, "delta_tau_mass": obs.delta_tau_mass},
            "gate": gate,
            "force": {"bloom": f_bloom, "effective": f_eff},
            "state": {"x": self.state.x, "last_force": self.state.last_force},
            "meta": dict(meta),
        }
        step_receipt = self.emit("BLOOMFORCE_STEP", payload)

        self.emit("TICK", {})
        self.state.tick += 1
        return self.state, step_receipt
