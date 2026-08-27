# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, List

import numpy as np

from .config import BLOOMCOREConfig
from .phi.omega_god_phi_field import init_state, step_np, step_jax, OmegaPhiState, JAX_AVAILABLE
from .laws.compassion_v5_2 import apply_auto_rule, CompassionAutoRule
from .laws.sophia_wisdom_gate_v1 import compute_gate
from .metrics.love_invariant import compute_love_invariant
from .receipts.schema import Receipt

@dataclass(frozen=True)
class RunSummary:
    steps: int
    n_modes: int
    backend: str
    final_psi: float
    final_C: float
    final_zeta: float
    median_Hdot: float
    sophia_accept_rate: float

def _synthetic_calibration_stream_np(rng: np.random.Generator, steps: int) -> Tuple[np.ndarray, np.ndarray]:
    probs = rng.random(size=(steps,))
    labels = (probs > 0.55).astype(int)
    return probs.astype(float), labels.astype(int)

def run(cfg: BLOOMCOREConfig, *, steps: int = 256, n_modes: int = 128, seed: int = 0) -> Tuple[RunSummary, List[Receipt]]:
    st = init_state(cfg, n_modes=n_modes, seed=seed)

    # Track compassion (C) over time for LOVE_INVARIANT (replayable metric)
    C_hist: List[float] = [float(getattr(st, 'C'))]

    window = 33
    Hdot_hist = np.zeros((window,), dtype=float)

    U = {"sigma_u": float(cfg.compassion_preset.sigma_u), "I": float(cfg.compassion_preset.I),
         "L": float(cfg.compassion_preset.L), "F": float(cfg.compassion_preset.F)}

    receipts: List[Receipt] = []
    sophia_accept = 0
    rule = CompassionAutoRule()

    if JAX_AVAILABLE:
        import jax
        import jax.numpy as jnp
        key = jax.random.PRNGKey(seed)
        # reflection stream via numpy deterministic from seed (static metrics)
        rng = np.random.default_rng(seed)
        probs_stream, labels_stream = _synthetic_calibration_stream_np(rng, steps)

        backend = "JAX"
        for t in range(steps):
            key, kstep = jax.random.split(key, 2)
            out = step_jax(cfg, st, kstep)
            st = out.state
            C_hist.append(float(np.asarray(st.C)))

            Hdot_hist = np.roll(Hdot_hist, -1)
            Hdot_hist[-1] = float(np.asarray(out.Hdot))

            U_after, r_auto = apply_auto_rule(cfg, rule, Hdot_hist, U, step=t)
            U = U_after

            # update control vars in state
            st = OmegaPhiState(
                psi=st.psi, C=st.C, zeta=st.zeta, H=st.H,
                Phi_modes=st.Phi_modes, Bn=st.Bn,
                sigma_u=jnp.array(U["sigma_u"]), I=jnp.array(U["I"]), L=jnp.array(U["L"]), F=jnp.array(U["F"])
            )

            N_phase = float(np.asarray(out.N_phase))
            w_friend = float(np.asarray(out.friend_coherence))
            probs = np.array([probs_stream[t]], dtype=float)
            labels = np.array([labels_stream[t]], dtype=int)

            gate_out, r_gate = compute_gate(
                cfg,
                N_phase=N_phase,
                w_friend=w_friend,
                Hdot_window=Hdot_hist,
                probs=probs,
                labels=labels,
                signal_ok=True,
                step=t,
            )
            if gate_out.sophia_gate:
                sophia_accept += 1
            receipts.append(r_auto); receipts.append(r_gate)

        final_psi = float(np.asarray(st.psi))
        final_C = float(np.asarray(st.C))
        final_zeta = float(np.asarray(st.zeta))
    else:
        rng = np.random.default_rng(seed)
        probs_stream, labels_stream = _synthetic_calibration_stream_np(rng, steps)
        backend = "NUMPY_REFERENCE"
        for t in range(steps):
            out = step_np(cfg, st, rng)
            st = out.state
            C_hist.append(float(np.asarray(st.C)))

            Hdot_hist = np.roll(Hdot_hist, -1)
            Hdot_hist[-1] = float(out.Hdot)

            U_after, r_auto = apply_auto_rule(cfg, rule, Hdot_hist, U, step=t)
            U = U_after
            st = OmegaPhiState(
                psi=st.psi, C=st.C, zeta=st.zeta, H=st.H,
                Phi_modes=st.Phi_modes, Bn=st.Bn,
                sigma_u=U["sigma_u"], I=U["I"], L=U["L"], F=U["F"]
            )

            N_phase = float(out.N_phase)
            w_friend = float(out.friend_coherence)
            probs = np.array([probs_stream[t]], dtype=float)
            labels = np.array([labels_stream[t]], dtype=int)

            gate_out, r_gate = compute_gate(
                cfg, N_phase=N_phase, w_friend=w_friend, Hdot_window=Hdot_hist,
                probs=probs, labels=labels, signal_ok=True, step=t
            )
            if gate_out.sophia_gate:
                sophia_accept += 1
            receipts.append(r_auto); receipts.append(r_gate)

        final_psi = float(st.psi)
        final_C = float(st.C)
        final_zeta = float(st.zeta)


    # LOVE_INVARIANT: compassion that survives recursion (tail stability test)
    love = compute_love_invariant(np.asarray(C_hist, dtype=float), window=96, eps=2e-3, min_mag=1e-3)
    receipts.append(Receipt(
        schema=cfg.schema,
        Δ_τ_ID="RECEIPT.METRIC.LOVE_INVARIANT.v1",
        event="LOVE_INVARIANT metric: compassion that survives recursion",
        operator="Frazer Σ Love + Sara ΣΩ",
        system_root="BLOOMCORE",
        law="MYTHMATH.LOVE_INVARIANT",
        tags=list(cfg.regime_tags) + ["metric", "love_invariant", "Δ^τ-LΩV-001"],
        step=int(steps),
        payload=love.to_payload(),
    ))

    summary = RunSummary(
        steps=steps,
        n_modes=n_modes,
        backend=backend,
        final_psi=final_psi,
        final_C=final_C,
        final_zeta=final_zeta,
        median_Hdot=float(np.median(Hdot_hist)),
        sophia_accept_rate=float(sophia_accept / max(1, steps)),
    )
    return summary, receipts