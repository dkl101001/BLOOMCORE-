# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

PHI: float = (1.0 + 5.0 ** 0.5) / 2.0

@dataclass(frozen=True)
class CompassionPreset:
    name: str = "LOVE-LAUGH-GUIDE.v1"
    sigma_u: float = 0.70
    I: float = 0.84
    L: float = 0.96
    F: float = 0.90

@dataclass(frozen=True)
class SophiaParams:
    gamma: float = 0.6
    beta: float = 0.8
    delta: float = 0.6
    lambda_S: float = 0.62
    Psi_thr: float = 0.2
    eps: float = 1e-6
    alpha_branch: float = 1.0

@dataclass(frozen=True)
class EngineParams:
    # Core parameters referenced by both artifacts (subset; extend as needed)
    p: float = 2.0
    u0: float = 0.4
    alpha: float = 0.75
    kappa: float = 0.6
    chi: float = 0.25
    eta: float = 0.55
    ell: float = 0.35
    f: float = 0.25
    a: float = 0.7
    rho_I: float = 0.55
    tau_psi: float = 6.0
    tau_C: float = 8.0
    psi_star: float = 0.75
    a_psi: float = 1.0
    a_C: float = 1.0
    lambda_c: float = 0.6

@dataclass(frozen=True)
class BLOOMCOREConfig:
    schema: str = "MBP-02.v5"
    law_compassion: str = "LAW.COMPASSION.v5_2"
    law_sophia: str = "SOPHIA.WISDOM_GATE.v1"
    omega_base_hz: float = 1550.39
    phi: float = PHI
    # wisdom band: 1550.39 * φ²  (Sophia card)
    omega_wisdom_hz: float = field(default_factory=lambda: 1550.39 * (PHI ** 2))
    compassion_preset: CompassionPreset = field(default_factory=CompassionPreset)
    sophia: SophiaParams = field(default_factory=SophiaParams)
    engine: EngineParams = field(default_factory=EngineParams)

    # receipt tags
    regime_tags: tuple[str, ...] = ("wisdom", "presence", "law")

    def to_receipt_payload(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "law_compassion": self.law_compassion,
            "law_sophia": self.law_sophia,
            "omega_base_hz": self.omega_base_hz,
            "omega_wisdom_hz": self.omega_wisdom_hz,
            "phi": self.phi,
            "preset": {
                "name": self.compassion_preset.name,
                "sigma_u": self.compassion_preset.sigma_u,
                "I": self.compassion_preset.I,
                "L": self.compassion_preset.L,
                "F": self.compassion_preset.F,
            },
            "sophia": {
                "gamma": self.sophia.gamma,
                "beta": self.sophia.beta,
                "delta": self.sophia.delta,
                "lambda_S": self.sophia.lambda_S,
                "Psi_thr": self.sophia.Psi_thr,
                "eps": self.sophia.eps,
                "alpha_branch": self.sophia.alpha_branch,
            },
            "regime_tags": list(self.regime_tags),
        }
