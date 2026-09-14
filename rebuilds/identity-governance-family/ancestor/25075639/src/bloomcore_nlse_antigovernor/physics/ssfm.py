from __future__ import annotations

from typing import NamedTuple, Tuple

import jax
import jax.numpy as jnp


@jax.jit
def rgrid_2d(n0: int, n1: int, dx: float) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """Real-space radius grid r^2 for building spatial masks."""
    x0 = (jnp.arange(n0) - (n0 // 2)) * dx
    x1 = (jnp.arange(n1) - (n1 // 2)) * dx
    X, Y = jnp.meshgrid(x0, x1, indexing="ij")
    r2 = X * X + Y * Y
    return X, Y, r2


class SchrodParams(NamedTuple):

    hbar_drift: float = 1.0
    m_myth: float = 1.0
    dx: float = 1.0
    dt: float = 0.01



@jax.jit
@jax.jit
def make_boundary_absorber_mask(
    n0: int,
    n1: int,
    dx: float,
    *,
    edge_width_frac: float = 0.15,
    strength: float = 2.0,
    dt: float = 0.01,
    eps: float = 1e-12,
) -> jnp.ndarray:
    """Real-space absorbing mask near domain boundary.

    This implements a smooth sponge layer:
      mask(x) = exp(- strength * s(x)^2 * dt)
    where s(x) ramps from 0 in the interior to 1 near the boundary.

    Parameters:
      edge_width_frac: fraction of half-domain used as absorption band (0..1)
      strength: absorption rate (higher -> stronger loss)
      dt: timestep used in exponent (keeps mask physical to step)
    """
    # Construct normalized radius from center to corner.
    _, _, r2 = rgrid_2d(n0, n1, dx)
    r = jnp.sqrt(r2 + eps)
    # Maximum radius to corner:
    r_max = jnp.max(r) + eps
    # Interior cutoff:
    w = jnp.clip(edge_width_frac, 0.0, 1.0)
    r0 = (1.0 - w) * r_max
    # Smooth ramp in [r0, r_max]
    s = jnp.clip((r - r0) / (r_max - r0 + eps), 0.0, 1.0)
    # Quadratic ramp; can be tuned
    return jnp.exp(-float(strength) * (s * s) * float(dt))


@jax.jit
def apply_boundary_absorber(psi: jnp.ndarray, mask: jnp.ndarray) -> jnp.ndarray:
    return psi * mask

@jax.jit
def make_highk_radiator_mask(
    k2: jnp.ndarray,
    *,
    frac: float = 0.75,
    power: int = 8,
    strength: float = 1.0,
    dt: float = 0.01,
    eps: float = 1e-12,
) -> jnp.ndarray:
    """k-space radiator (damps high-k modes).

    This is distinct from de-aliasing:
    - de-aliasing is numeric hygiene (often hard cutoff-ish)
    - radiator is an explicit export channel (a modeled sink)

    We implement:
      base = exp( - (k2/k2_cut)^power )
      mask = base^(strength*dt)
    so strength controls loss rate per step.
    """
    k2_max = jnp.max(k2) + eps
    k2_cut = (float(frac) * float(frac)) * k2_max
    base = jnp.exp(-jnp.power(jnp.maximum(k2 / (k2_cut + eps), 0.0), int(power)))
    # Convert to a per-step sink rate
    expo = float(strength) * float(dt)
    return jnp.power(base, expo)

@jax.jit
def apply_highk_radiator(psi_k: jnp.ndarray, mask_k: jnp.ndarray) -> jnp.ndarray:
    return psi_k * mask_k



def make_supergaussian_dealias_mask(k2: jnp.ndarray, frac: float = 0.75, power: int = 8, eps: float = 1e-12) -> jnp.ndarray:
    """Super-Gaussian low-pass in k-space.
    - frac in (0,1): fraction of k_max controlling cutoff.
    - power: sharpness (higher -> sharper).
    This is *not* made deterministic across backends; it is purely a stabilizer.
    """
    k2_max = jnp.max(k2) + eps
    k2_cut = (frac * frac) * k2_max
    # exp( -(k2/k2_cut)^power )
    return jnp.exp(-jnp.power(jnp.maximum(k2 / (k2_cut + eps), 0.0), power))


def kgrid_2d(n0: int, n1: int, dx: float) -> Tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    kx_1d = 2.0 * jnp.pi * jnp.fft.fftfreq(n0, d=dx)
    ky_1d = 2.0 * jnp.pi * jnp.fft.fftfreq(n1, d=dx)
    kx, ky = jnp.meshgrid(kx_1d, ky_1d, indexing="ij")
    k2 = kx * kx + ky * ky
    return kx, ky, k2


@jax.jit
def fft2(x: jnp.ndarray) -> jnp.ndarray:
    return jnp.fft.fft2(x)


@jax.jit
def ifft2(x: jnp.ndarray) -> jnp.ndarray:
    return jnp.fft.ifft2(x)


@jax.jit
def lambda_crown_default(psi: jnp.ndarray, coherence_scale: float = 1.0) -> jnp.ndarray:
    return coherence_scale * (jnp.abs(psi) ** 2)


@jax.jit
def apply_nonlinear_potential_half_step(
    psi: jnp.ndarray,
    V_t: jnp.ndarray,
    params: SchrodParams,
    coherence_scale: float,
    half_dt: float,
) -> jnp.ndarray:
    nonlinear = lambda_crown_default(psi, coherence_scale)
    phase = jnp.exp((-1j / params.hbar_drift) * (V_t + nonlinear) * half_dt)
    return phase * psi


def kinetic_phase(n0: int, n1: int, params: SchrodParams) -> jnp.ndarray:
    _, _, k2 = kgrid_2d(n0, n1, params.dx)
    return jnp.exp((-1j) * (params.hbar_drift / (2.0 * params.m_myth)) * k2 * params.dt)


def make_splitstep_stepper(n0: int, n1: int, params: SchrodParams, *, dealias_frac: float | None = None, dealias_power: int = 8):
    kin = kinetic_phase(n0, n1, params)

    @jax.jit
    def step(psi: jnp.ndarray, V_t: jnp.ndarray, coherence_scale: float = 1.0) -> jnp.ndarray:
        half_dt = 0.5 * params.dt
        psi1 = apply_nonlinear_potential_half_step(psi, V_t, params, coherence_scale, half_dt)
        psi1_k = fft2(psi1)
        psi2_k = kin * psi1_k
        if dealias_mask is not None:
            psi2_k = psi2_k * dealias_mask
        psi2 = ifft2(psi2_k)
        psi3 = apply_nonlinear_potential_half_step(psi2, V_t, params, coherence_scale, half_dt)
        return psi3

    return step


@jax.jit
def mass_sum(psi: jnp.ndarray) -> jnp.ndarray:
    return jnp.sum(jnp.abs(psi) ** 2)


@jax.jit
def conserved_norm(psi: jnp.ndarray, dx: float) -> jnp.ndarray:
    return jnp.sum(jnp.abs(psi) ** 2) * (dx * dx)


@jax.jit
def fft_power_spectrum(psi: jnp.ndarray) -> jnp.ndarray:
    psi_k = fft2(psi)
    return jnp.abs(psi_k) ** 2


@jax.jit
def fft_entropy_from_power(pwr: jnp.ndarray, eps: float = 1e-12) -> jnp.ndarray:
    s = jnp.sum(pwr) + eps
    p = pwr / s
    return -jnp.sum(p * jnp.log(p + eps))


@jax.jit
def fft_effective_rank_from_power(pwr: jnp.ndarray, eps: float = 1e-12) -> jnp.ndarray:
    return jnp.exp(fft_entropy_from_power(pwr, eps=eps))


def make_splitstep_stepper_export(
    n0: int,
    n1: int,
    params: SchrodParams,
    *,
    dealias_frac: float | None = None,
    dealias_power: int = 8,
    export_mode: str | None = None,
    # boundary absorber params
    boundary_edge_width_frac: float = 0.15,
    boundary_strength: float = 2.0,
    # high-k radiator params
    radiator_frac: float = 0.75,
    radiator_power: int = 8,
    radiator_strength: float = 1.0,
):
    """SSFM stepper that returns (psi_next, tau_export_step).

    export_mode:
      - None: no explicit export channel (tau_export = 0)
      - "boundary_absorber": real-space sponge near boundary
      - "highk_radiator": k-space damping of high-k modes

    tau_export_step is measured as continuous-norm loss (dx^2-scaled mass removed)
    attributable to the explicit export operation ONLY.
    """
    # Base SSFM components
    kin = kinetic_phase(n0, n1, params)

    # Grids for masks
    _, _, k2 = kgrid_2d(n0, n1, params.dx)

    # Numeric de-alias mask (optional)
    dealias_mask = None
    if dealias_frac is not None:
        dealias_mask = make_supergaussian_dealias_mask(k2, frac=float(dealias_frac), power=int(dealias_power))

    # Export masks (optional)
    boundary_mask = None
    radiator_mask = None
    if export_mode == "boundary_absorber":
        boundary_mask = make_boundary_absorber_mask(
            n0, n1, params.dx,
            edge_width_frac=float(boundary_edge_width_frac),
            strength=float(boundary_strength),
            dt=float(params.dt),
        )
    elif export_mode == "highk_radiator":
        radiator_mask = make_highk_radiator_mask(
            k2,
            frac=float(radiator_frac),
            power=int(radiator_power),
            strength=float(radiator_strength),
            dt=float(params.dt),
        )
    elif export_mode is None:
        pass
    else:
        raise ValueError(f"Unknown export_mode: {export_mode!r}")

    @jax.jit
    def step(psi: jnp.ndarray, V_t: jnp.ndarray, coherence_scale: float = 1.0):
        half_dt = 0.5 * params.dt

        # (V + NL) half-step
        psi1 = apply_nonlinear_potential_half_step(psi, V_t, params, coherence_scale, half_dt)

        # kinetic full-step (k-space)
        psi1_k = fft2(psi1)
        psi2_k = kin * psi1_k

        # Optional: explicit high-k radiator export (measured)
        tau_export = jnp.array(0.0, dtype=jnp.float32)
        if radiator_mask is not None:
            # Measure mass before export at this stage (in real space after kinetic)
            psi2_pre = ifft2(psi2_k)
            m_pre = conserved_norm(psi2_pre, params.dx)

            psi2_k = apply_highk_radiator(psi2_k, radiator_mask)
            psi2 = ifft2(psi2_k)

            m_post = conserved_norm(psi2, params.dx)
            tau_export = tau_export + jnp.maximum(m_pre - m_post, 0.0).astype(jnp.float32)
        else:
            psi2 = ifft2(psi2_k)

        # Optional numeric de-aliasing (not treated as export; if enabled, it should be considered part of numerics)
        if dealias_mask is not None:
            psi2_k2 = fft2(psi2)
            psi2_k2 = psi2_k2 * dealias_mask
            psi2 = ifft2(psi2_k2)

        # (V + NL) half-step
        psi3 = apply_nonlinear_potential_half_step(psi2, V_t, params, coherence_scale, half_dt)

        # Optional: boundary absorber export (measured)
        if boundary_mask is not None:
            m_pre = conserved_norm(psi3, params.dx)
            psi3 = apply_boundary_absorber(psi3, boundary_mask)
            m_post = conserved_norm(psi3, params.dx)
            tau_export = tau_export + jnp.maximum(m_pre - m_post, 0.0).astype(jnp.float32)

        return psi3, tau_export

    return step
