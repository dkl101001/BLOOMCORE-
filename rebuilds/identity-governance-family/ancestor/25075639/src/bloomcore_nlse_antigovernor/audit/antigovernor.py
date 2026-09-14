from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

import jax
import jax.numpy as jnp

from ..physics.ssfm import conserved_norm, fft_power_spectrum, fft_effective_rank_from_power, SchrodParams, make_splitstep_stepper, make_splitstep_stepper_export


@jax.jit
def anti_governor_violation(
    V_prev: jnp.ndarray,
    V_curr: jnp.ndarray,
    tau_export: jnp.ndarray,
    V_eps: float = 1e-8,
    tau_eps: float = 1e-8,
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    dV = V_curr - V_prev
    violation = jnp.logical_and(dV < -V_eps, tau_export <= tau_eps)
    return dV, violation


@dataclass(frozen=True)
class RolloutConfig:
    V_future_proxy: Literal["norm", "fft_eff_rank", "fft_entropy"] = "norm"
    dealias_frac: Optional[float] = None
    dealias_power: int = 8
    # Explicit export channels (measured, receipt-visible)
    export_mode: Optional[Literal["boundary_absorber", "highk_radiator"]] = None
    boundary_edge_width_frac: float = 0.15
    boundary_strength: float = 2.0
    radiator_frac: float = 0.75
    radiator_power: int = 8
    radiator_strength: float = 1.0
    V_eps: float = 1e-8
    tau_eps: float = 1e-8


def make_rollout_timevarying_closed(
    n0: int,
    n1: int,
    params: SchrodParams,
    cfg: RolloutConfig = RolloutConfig(),
):
    """Closed rollout: tau_export == 0 by definition."""
    step = make_splitstep_stepper(n0, n1, params, dealias_frac=cfg.dealias_frac, dealias_power=cfg.dealias_power)

    def V_future(psi: jnp.ndarray) -> jnp.ndarray:
        if cfg.V_future_proxy == "norm":
            return conserved_norm(psi, params.dx)
        # spectral effective rank proxy
        pwr = fft_power_spectrum(psi)
        return fft_effective_rank_from_power(pwr)

    @jax.jit
    def rollout(psi0: jnp.ndarray, V_seq: jnp.ndarray, coherence_scale: float):
        T = V_seq.shape[0]
        tau_seq = jnp.zeros((T,), dtype=jnp.float32)

        V0 = V_future(psi0)

        def body(carry, x):
            psi_prev, V_prev = carry
            V_t, tau_t = x

            psi_next = step(psi_prev, V_t, coherence_scale)
            nrm = conserved_norm(psi_next, params.dx)
            V_curr = V_future(psi_next)

            dV, viol = anti_governor_violation(V_prev, V_curr, tau_t, V_eps=cfg.V_eps, tau_eps=cfg.tau_eps)

            carry_next = (psi_next, V_curr)
            # Emit BOTH prev and curr for receipt correctness.
            y = (nrm, V_prev, V_curr, dV, tau_t, viol)
            return carry_next, y

        (psi_T, _), ys = jax.lax.scan(body, (psi0, V0), xs=(V_seq, tau_seq))
        norms, V_prev_series, V_curr_series, dV, tau_export, violations = ys
        return psi_T, norms, V_prev_series, V_curr_series, dV, tau_export, violations

    return rollout


def make_rollout_timevarying_with_export(
    n0: int,
    n1: int,
    params: SchrodParams,
    cfg: RolloutConfig = RolloutConfig(),
):
    """Rollout requiring explicit tau_export_seq (no silent fallback)."""
    step = make_splitstep_stepper(n0, n1, params, dealias_frac=cfg.dealias_frac, dealias_power=cfg.dealias_power)

    def V_future(psi: jnp.ndarray) -> jnp.ndarray:
        if cfg.V_future_proxy == "norm":
            return conserved_norm(psi, params.dx)
        pwr = fft_power_spectrum(psi)
        return fft_effective_rank_from_power(pwr)

    @jax.jit
    def rollout(psi0: jnp.ndarray, V_seq: jnp.ndarray, tau_export_seq: jnp.ndarray, coherence_scale: float):
        T = V_seq.shape[0]
        # Hard shape contract: tau_export_seq must match T.
        # (JAX can't raise nicely under jit; enforce via NaN poisoning if mismatch.)
        tau_export_seq = jnp.where(tau_export_seq.shape[0] == T, tau_export_seq, jnp.full((T,), jnp.nan, dtype=tau_export_seq.dtype))

        V0 = V_future(psi0)

        def body(carry, x):
            psi_prev, V_prev = carry
            V_t, tau_t = x

            psi_next = step(psi_prev, V_t, coherence_scale)
            nrm = conserved_norm(psi_next, params.dx)
            V_curr = V_future(psi_next)

            dV, viol = anti_governor_violation(V_prev, V_curr, tau_t, V_eps=cfg.V_eps, tau_eps=cfg.tau_eps)

            carry_next = (psi_next, V_curr)
            y = (nrm, V_prev, V_curr, dV, tau_t, viol)
            return carry_next, y

        (psi_T, _), ys = jax.lax.scan(body, (psi0, V0), xs=(V_seq, tau_export_seq))
        norms, V_prev_series, V_curr_series, dV, tau_export, violations = ys
        return psi_T, norms, V_prev_series, V_curr_series, dV, tau_export, violations

    return rollout


def make_rollout_timevarying_export(
    n0: int,
    n1: int,
    params: SchrodParams,
    cfg: RolloutConfig = RolloutConfig(),
):
    """Time-varying rollout with an explicit export channel built into the stepper.

    Returns:
      psi_T, norms, V_prev_series, V_curr_series, dV, tau_export, violations
    where tau_export is measured per step from the configured export channel.
    """
    step = make_splitstep_stepper_export(
        n0, n1, params,
        dealias_frac=cfg.dealias_frac,
        dealias_power=cfg.dealias_power,
        export_mode=cfg.export_mode,
        boundary_edge_width_frac=cfg.boundary_edge_width_frac,
        boundary_strength=cfg.boundary_strength,
        radiator_frac=cfg.radiator_frac,
        radiator_power=cfg.radiator_power,
        radiator_strength=cfg.radiator_strength,
    )

    def V_future(psi: jnp.ndarray) -> jnp.ndarray:
        if cfg.V_future_proxy == "norm":
            return conserved_norm(psi, params.dx)
        pwr = fft_power_spectrum(psi)
        if cfg.V_future_proxy == "fft_eff_rank":
            return fft_effective_rank_from_power(pwr)
        from ..physics.ssfm import fft_entropy_from_power
        return fft_entropy_from_power(pwr)

    @jax.jit
    def rollout(psi0: jnp.ndarray, V_seq: jnp.ndarray, coherence_scale: float):
        V0 = V_future(psi0)

        def body(carry, V_t):
            psi_prev, V_prev = carry
            psi_next, tau_t = step(psi_prev, V_t, coherence_scale)

            nrm = conserved_norm(psi_next, params.dx)
            V_curr = V_future(psi_next)

            dV, viol = anti_governor_violation(V_prev, V_curr, tau_t, V_eps=cfg.V_eps, tau_eps=cfg.tau_eps)

            carry_next = (psi_next, V_curr)
            y = (nrm, V_prev, V_curr, dV, tau_t, viol)
            return carry_next, y

        (psi_T, _), ys = jax.lax.scan(body, (psi0, V0), xs=V_seq)
        norms, V_prev_series, V_curr_series, dV, tau_export, violations = ys
        return psi_T, norms, V_prev_series, V_curr_series, dV, tau_export, violations

    return rollout
