# ============================================================
# Section 6 Response Vector (Agent) v2 — AetherLoom Hardened
# Title: ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)
# ============================================================

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, Literal
import math
import random
import secrets

ActionAtomKind = Literal[
    "minimize_directional",
    "increase_convexity",
    "increase_liquidity_preference",
    "deprioritize_trend_commitment",
    "increase_diversification_bias",
    "increase_hedge_bias",
    "reduce_beta_exposure",
    "wait_for_confirmation",
    "favor_dispersion_aware_exposure",
]

@dataclass(frozen=True)
class ActionAtom:
    kind: ActionAtomKind
    weight: float = 1.0
    meta: Dict[str, Any] = field(default_factory=dict)

ATOM_PHRASES: Dict[ActionAtomKind, List[str]] = {
    "minimize_directional": [
        "keeps directional exposure minimal",
        "holds minimal directional exposure",
        "maintains a low directional stance",
    ],
    "increase_convexity": [
        "raises convex protection preference",
        "tilts toward convex protection",
        "leans into convexity over linear exposure",
    ],
    "increase_liquidity_preference": [
        "prefers liquidity and rapid reconfiguration",
        "elevates liquidity preference to preserve flexibility",
        "keeps liquidity high to enable fast reconfiguration",
    ],
    "deprioritize_trend_commitment": [
        "deprioritizes trend commitments under current coherence",
        "keeps trend commitment low while coherence is constrained",
        "avoids trend lock-in while the regime remains unstable",
    ],
    "increase_diversification_bias": [
        "increases diversification bias across proxies",
        "spreads exposure across non-identical proxy pathways",
        "raises diversification bias to reduce single-axis risk",
    ],
    "increase_hedge_bias": [
        "raises hedge bias relative to baseline",
        "keeps hedge bias elevated versus prior regime",
        "increases hedge bias to absorb tail risk",
    ],
    "reduce_beta_exposure": [
        "reduces beta exposure bias",
        "keeps beta exposure suppressed",
        "lowers beta exposure preference under current stress",
    ],
    "wait_for_confirmation": [
        "waits for confirmation from vol and rates before shifting posture",
        "requires confirmation signals before increasing commitment",
        "holds until confirmation arrives from cross-asset structure",
    ],
    "favor_dispersion_aware_exposure": [
        "favors dispersion-aware exposure selection",
        "tilts toward dispersion-aware selection rather than broad exposure",
        "prefers dispersion-aware selection in mixed regimes",
    ],
}

ATOM_TO_VECTOR: Dict[ActionAtomKind, Dict[str, float]] = {
    "increase_diversification_bias": {"diversification_bias": 1.0},
    "increase_hedge_bias": {"hedge_bias": 1.0},
    "reduce_beta_exposure": {"beta_exposure_bias": -1.0},
    "minimize_directional": {"beta_exposure_bias": -0.7},
    "increase_liquidity_preference": {"liquidity_preference": 1.0},
    "increase_convexity": {"optionality_preference": 1.0},
    "deprioritize_trend_commitment": {"optionality_preference": 0.6, "beta_exposure_bias": -0.2},
    "wait_for_confirmation": {"liquidity_preference": 0.3, "optionality_preference": 0.4},
    "favor_dispersion_aware_exposure": {"diversification_bias": 0.6, "hedge_bias": 0.2},
}

def _nonce() -> str:
    return secrets.token_hex(16)

def _rng(n: str) -> random.Random:
    return random.Random(n)

def _sigmoid(x: float) -> float:
    # clamp protects exp overflow; preserves monotonic mapping
    if x > 40.0:
        return 1.0
    if x < -40.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))

def _sanitize_text(s: str) -> str:
    banned = ("buy", "sell", "enter", "exit", "allocate", "rebalance", "short", "long")
    st = s.strip()
    low = st.lower()
    for b in banned:
        if low == b or low.startswith(b + " "):
            return "sim_" + st
    return st

def _sanitize_technical_params(tp: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not tp:
        return {}
    banned = ("buy", "sell", "enter", "exit", "allocate", "rebalance", "short", "long")
    out: Dict[str, Any] = {}
    for k, v in tp.items():
        kk = str(k).strip()
        if any(kk.lower().startswith(p) for p in banned):
            kk = f"sim_{kk}"
        if isinstance(v, str):
            out[kk] = _sanitize_text(v)
        else:
            out[kk] = v
    return out

def compute_vector(atoms: Sequence[ActionAtom]) -> Dict[str, float]:
    acc = {
        "diversification_bias": 0.0,
        "hedge_bias": 0.0,
        "beta_exposure_bias": 0.0,
        "liquidity_preference": 0.0,
        "optionality_preference": 0.0,
    }
    for a in atoms:
        w_map = ATOM_TO_VECTOR.get(a.kind, {})
        for k, w in w_map.items():
            acc[k] += float(a.weight) * float(w)
    return {k: _sigmoid(v) for k, v in acc.items()}

# --- Simple Coherence Matrix Governor (style-only, non-actionable) ---
def coherence_matrix(
    coherence: float,
    fragility_index: float,
    *,
    coherence_gate: float,
    fragility_gate: float = 0.60,
) -> Tuple[str, float]:
    hi_c = coherence >= coherence_gate
    hi_f = fragility_index >= fragility_gate

    if hi_c and (not hi_f):
        return ("clear", 1.05)
    if hi_c and hi_f:
        return ("braced", 0.95)
    if (not hi_c) and hi_f:
        return ("gated", 0.80)
    return ("soft_gated", 0.90)

def build_response_vector_v2(
    posture: str,
    action_atoms: Sequence[ActionAtom],
    coherence: float,
    *,
    ctx: Any = None,
    eq_id: Optional[str] = None,
    coherence_gate: float = 0.60,
    fragility_index: float = 0.50,
    fragility_gate: float = 0.60,
    technical_params: Optional[Dict[str, Any]] = None,
    nonce: Optional[str] = None,
) -> Dict[str, Any]:

    atoms = sorted(list(action_atoms), key=lambda x: (x.kind, -x.weight))

    style, w_mul = coherence_matrix(
        coherence=coherence,
        fragility_index=fragility_index,
        coherence_gate=coherence_gate,
        fragility_gate=fragility_gate,
    )

    governed_atoms = [ActionAtom(a.kind, weight=a.weight * w_mul, meta=a.meta) for a in atoms]

    n = nonce or _nonce()
    rng = _rng(n)

    picks: List[Dict[str, Any]] = []
    phrases: List[str] = []

    if not governed_atoms:
        phrases = ["holds a baseline simulation posture"]
    else:
        for a in governed_atoms:
            variants = ATOM_PHRASES.get(a.kind, [f"encodes atom {a.kind}"])
            idx = rng.randrange(len(variants))
            picks.append({"kind": a.kind, "variant_idx": idx, "weight": a.weight})
            phrases.append(variants[idx])

    if style in ("clear", "braced"):
        c_opts = ["until coherence stabilizes"]
    else:
        c_opts = ["until coherence clears constraint"]

    c_idx = rng.randrange(len(c_opts))
    plain = "The agent " + ", ".join(phrases) + f", {c_opts[c_idx]}."

    vec = compute_vector(governed_atoms)
    tech = _sanitize_technical_params(technical_params)

    payload: Dict[str, Any] = {
        "type": "simulated_agent_transition",
        "scope": "simulation_only",
        "permissions": "non_executable",
        "label": "AetherLoom response (Regime-consistent)",
        "vector": vec,
        "plain_language": plain,
        "technical_parameters": tech,
        "nonce": n,
        "picks": picks,
        "coherence_style": style,
        "posture_agent": posture,
        "governor": {"kind": "COHERENCE_MATRIX_2x2", "weight_multiplier": w_mul},
    }

    if ctx:
        receipt = {**payload, "intent": "modeled_agent_state", "generator": "v2.0.1"}
        if eq_id:
            receipt["eq_id"] = eq_id
        ctx.emit("OPEN.SECTION6.RESPONSE_VECTOR.v2", receipt)

    return payload
