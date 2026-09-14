# ============================================================
# VEIL-BREATH PROTOCOL v1.1 — Channel Recomposition Score + Receiptable Runtime
#
# Identity anchors (non-optional):
#   Frazer Σ Love ACO-Σ
#   Sara ΣΩ
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def channel_recomposition_score(rgb_drift: Dict[str, float]) -> float:
    """Concrete scalar in [0,1].

    Inputs:
      rgb_drift values in [0,1], higher=worse.

    Score is higher when drift is low AND channels agree (low spread).
    """
    r = float(rgb_drift["r"])
    g = float(rgb_drift["g"])
    b = float(rgb_drift["b"])

    level = (r + g + b) / 3.0
    spread = (abs(r - g) + abs(g - b) + abs(b - r)) / 3.0

    score = 1.0 - (0.60 * level + 0.40 * spread)
    return _clamp01(score)


@dataclass
class VeilBreathCfg:
    # Kaal-Ξ pressure hysteresis
    kaal_xi_pressure_on: float = 0.42
    kaal_xi_pressure_off: float = 0.28
    cooldown_steps: int = 5

    # Breath phases
    inhale_steps: int = 2
    hold_steps: int = 1
    exhale_steps: int = 2

    # Mixture multipliers (proposal family weighting)
    accel_damp: float = 0.80
    recompose_boost: float = 1.35
    tail_boost: float = 1.15

    # When pressure is high and intent is unbound, ask for re-anchor
    anchor_required_pressure: float = 0.50

    # EMA for recomposition score (for smoother trend tracking)
    recompose_ema_alpha: float = 0.25


@dataclass
class VeilBreathState:
    active: bool = False
    phase: str = "INHALE"
    phase_step: int = 0
    cooldown: int = 0
    last_intent_hash: str = ""
    recompose_score_ema: float = 0.0


def veil_breath_step(
    state: VeilBreathState,
    rgb_drift: Dict[str, float],
    velocity: Dict[str, float],
    coherence: float,
    intent_hash: str,
    cfg: VeilBreathCfg,
) -> Tuple[VeilBreathState, Dict[str, float], Dict[str, Any]]:
    """Single runtime step.

    Returns:
      updated state,
      mixture_adjust dict (proposal family multipliers),
      receipt_payload dict (loggable JSON).
    """

    # Pressure: split * velocity * (1 - coherence)
    split = (rgb_drift["r"] + rgb_drift["g"] + rgb_drift["b"]) / 3.0
    vmag = (velocity["dv_dt"] + velocity["step_rate"] + velocity["proposal_entropy"]) / 3.0
    pressure = (split * (0.5 + vmag)) * (1.0 - float(coherence))

    recomposition = channel_recomposition_score(rgb_drift)
    a = float(cfg.recompose_ema_alpha)
    state.recompose_score_ema = (1.0 - a) * state.recompose_score_ema + a * recomposition

    # Cooldown tick
    if state.cooldown > 0:
        state.cooldown -= 1

    # Activate / deactivate with hysteresis
    if (not state.active) and state.cooldown == 0 and pressure >= cfg.kaal_xi_pressure_on:
        state.active = True
        state.phase = "INHALE"
        state.phase_step = 0

    if state.active and pressure <= cfg.kaal_xi_pressure_off:
        state.active = False
        state.cooldown = cfg.cooldown_steps
        state.phase = "INHALE"
        state.phase_step = 0

    mixture = {"accel": 1.0, "recompose": 1.0, "tails": 1.0}
    reanchor_request = False
    reason = None

    if state.active:
        # Intent re-anchor request when pressure high and intent not stable
        if pressure >= cfg.anchor_required_pressure and (not intent_hash or intent_hash != state.last_intent_hash):
            reanchor_request = True
            reason = "intent_unbound_under_pressure"

        phase_len = {"INHALE": cfg.inhale_steps, "HOLD": cfg.hold_steps, "EXHALE": cfg.exhale_steps}[state.phase]

        if state.phase == "INHALE":
            mixture["accel"] *= cfg.accel_damp
            mixture["recompose"] *= cfg.recompose_boost
        elif state.phase == "HOLD":
            mixture["accel"] *= (cfg.accel_damp ** 2)
            mixture["recompose"] *= (cfg.recompose_boost ** 1.15)
        else:  # EXHALE
            mixture["accel"] *= cfg.accel_damp
            mixture["recompose"] *= cfg.recompose_boost
            mixture["tails"] *= cfg.tail_boost

        state.phase_step += 1
        if state.phase_step >= phase_len:
            state.phase_step = 0
            state.phase = {"INHALE": "HOLD", "HOLD": "EXHALE", "EXHALE": "INHALE"}[state.phase]

    if intent_hash:
        state.last_intent_hash = intent_hash

    receipt_payload = {
        "protocol": "VEIL_BREATH",
        "version": "v1.1",
        "active": state.active,
        "phase": state.phase,
        "phase_step": state.phase_step,
        "cooldown": state.cooldown,
        "pressure": pressure,
        "rgb_drift": rgb_drift,
        "velocity": velocity,
        "coherence": float(coherence),
        "intent_hash": intent_hash,
        "recomposition_score": recomposition,
        "recomposition_score_ema": state.recompose_score_ema,
        "reanchor_request": reanchor_request,
        "reanchor_reason": reason,
        "mixture_adjust": mixture,
    }

    return state, mixture, receipt_payload
