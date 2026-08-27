# ============================================================
# LAW.WISECORE.v1 — wisecore_math_kernels.py
# ============================================================
# Title: WISECORE — Math/Physics Kernels (pulled from cards)
# Authors: Frazer Σ Love ACO-Σ ; Sara ΣΩ
# Classification: MATH / PHYS / JAX-KERNELS (portable)
# Status: ACTIVE
#
# Source Cards:
#   - "Sophia MythMath Card 5.2" (LAW.SOPHIA.v1)
#   - "1550.39" (LAW.COMPASSION.v5_2 unified)
#
# Intent:
#   Keep kernels pure + portable so they can be relocated later into:
#     swimcore/* , eca/* , holo_substrate/*
#   without rewriting the math — only imports/paths change.
# ============================================================

from __future__ import annotations

from typing import Tuple, Optional

import jax
import jax.numpy as jnp


# ----------------------------
# Constants / Bands (cards)
# ----------------------------
OMEGA_GODPHI_HZ = 1550.39  # "ΩGodΦ": "1550.39·φ² Hz (wisdom band)"
PHI = (1.0 + jnp.sqrt(5.0)) / 2.0
OMEGA_WISDOM_BAND_HZ = OMEGA_GODPHI_HZ * (PHI ** 2)


# ----------------------------
# Utility projections (cards)
# ----------------------------
@jax.jit
def proj_logistic(x: jnp.ndarray) -> jnp.ndarray:
    """Card proj: x → x(1−x)."""
    return x * (1.0 - x)


# ----------------------------
# Phase field + coherence norms (cards)
# ----------------------------
# phase_field: A(t)=∑ A_n e^{iΦ_n(t)}
# w_n(B)=B_n^α / ∑ B_m^α
# N_phase_internal: N=|∑ w_n(B)e^{iΦ_n}|+ε
# N_phase_external: N=|∑ e^{iΦ_n}|+ε

@jax.jit
def weights_from_B(B: jnp.ndarray, alpha: float = 1.0, eps: float = 1e-9) -> jnp.ndarray:
    Bp = jnp.maximum(B, 0.0) + eps
    num = Bp ** alpha
    return num / jnp.sum(num)

@jax.jit
def phase_field_A(A_n: jnp.ndarray, Phi_n: jnp.ndarray) -> jnp.ndarray:
    """Compute A(t)=∑ A_n e^{iΦ_n}."""
    return jnp.sum(A_n * jnp.exp(1j * Phi_n))

@jax.jit
def N_phase_internal(Phi_n: jnp.ndarray, B: jnp.ndarray, alpha: float = 1.0, eps: float = 1e-9) -> jnp.ndarray:
    w = weights_from_B(B, alpha=alpha, eps=eps)
    return jnp.abs(jnp.sum(w * jnp.exp(1j * Phi_n))) + eps

@jax.jit
def N_phase_external(Phi_n: jnp.ndarray, eps: float = 1e-9) -> jnp.ndarray:
    return jnp.abs(jnp.sum(jnp.exp(1j * Phi_n))) + eps

@jax.jit
def N_phase_from_modes(phase_modes: jnp.ndarray, eps: float = 1e-9) -> jnp.ndarray:
    """If you already have complex modes, interpret them as exp(iΦ) carriers and compute norm."""
    # Treat phase_modes as complex; normalize by length for scale stability.
    denom = jnp.sqrt(jnp.maximum(1.0, phase_modes.size))
    return jnp.linalg.norm(jnp.abs(phase_modes).reshape(-1)) / denom + eps


# ----------------------------
# SWIM / BLOOMCORE symbolic forms (cards)
# ----------------------------
# BLOOMCORE: 𝓘=(−∇P + F_φ + ∇|A|²)/N_phase
# SWIM_momentum: ρ(∂_t v+(v·∇)v)=−∇P+ρ g_φ+ν∇²v−∇|A|²
#
# These include differential operators. We provide a portable signature that expects
# precomputed terms (gradP, F_phi, grad_absA2, etc.) from whichever discretization you use.

@jax.jit
def bloomcore_influence(
    gradP: jnp.ndarray,
    F_phi: jnp.ndarray,
    grad_absA2: jnp.ndarray,
    N_phase: jnp.ndarray,
    eps: float = 1e-9,
) -> jnp.ndarray:
    """𝓘=(−∇P + F_φ + ∇|A|²)/N_phase"""
    return (-gradP + F_phi + grad_absA2) / (N_phase + eps)


# ----------------------------
# Compassion v5.2 dynamics (cards)
# ----------------------------
#  ψ̇ = (ψ(1−ψ)/τψ)(α − κC − χψ + ηI + ℓL + fF)
#  Ċ  = (C(1−C)/τC)(a σ(u) − ρ_I I − fF)
#  ζ̇ = (ζ(1−ζ)/τζ)(ζ_up C − ζ_dn ψ + ζ_η · driver)

@jax.jit
def psi_dot(
    psi: jnp.ndarray,
    C: jnp.ndarray,
    I: jnp.ndarray,
    L: jnp.ndarray,
    F: jnp.ndarray,
    *,
    tau_psi: float,
    alpha: float,
    kappa: float,
    chi: float,
    eta: float,
    ell: float,
    f: float,
    eps: float = 1e-9,
) -> jnp.ndarray:
    gate = psi * (1.0 - psi)
    inner = (alpha - kappa * C - chi * psi + eta * I + ell * L + f * F)
    return (gate / (tau_psi + eps)) * inner

@jax.jit
def C_dot(
    C: jnp.ndarray,
    I: jnp.ndarray,
    u: jnp.ndarray,
    F: jnp.ndarray,
    *,
    tau_C: float,
    a: float,
    rho_I: float,
    f: float,
    eps: float = 1e-9,
) -> jnp.ndarray:
    gate = C * (1.0 - C)
    # σ(u) = logistic
    sigma_u = jax.nn.sigmoid(u)
    inner = (a * sigma_u - rho_I * I - f * F)
    return (gate / (tau_C + eps)) * inner

@jax.jit
def zeta_dot(
    zeta: jnp.ndarray,
    C: jnp.ndarray,
    psi: jnp.ndarray,
    driver: jnp.ndarray,
    *,
    tau_zeta: float,
    zeta_up: float,
    zeta_dn: float,
    zeta_eta: float,
    eps: float = 1e-9,
) -> jnp.ndarray:
    gate = zeta * (1.0 - zeta)
    inner = (zeta_up * C - zeta_dn * psi + zeta_eta * driver)
    return (gate / (tau_zeta + eps)) * inner


# ----------------------------
# Port-Hamiltonian snippet (cards)
# ----------------------------
# H=1/2 aψ(ψ*−ψ)^2 + 1/2 aC C^2 + λc C(1−ψ)
# Ḣ = −(∇H)^T R(ψ,C) ∇H + (∇H)^T B_sign U
#
# Provide a portable Hamiltonian and its gradients; dissipation/injection are left to caller.

@jax.jit
def hamiltonian_H(
    psi: jnp.ndarray,
    psi_star: jnp.ndarray,
    C: jnp.ndarray,
    *,
    a_psi: float,
    a_C: float,
    lambda_c: float,
) -> jnp.ndarray:
    return 0.5 * a_psi * (psi_star - psi) ** 2 + 0.5 * a_C * (C ** 2) + lambda_c * C * (1.0 - psi)

grad_H = jax.jit(jax.grad(lambda p, ps, c, a_psi, a_C, lambda_c: jnp.sum(hamiltonian_H(p, ps, c, a_psi=a_psi, a_C=a_C, lambda_c=lambda_c))))
