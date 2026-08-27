import jax
import jax.numpy as jnp

from bloomcore_nlse_antigovernor.physics.ssfm import SchrodParams, conserved_norm
from bloomcore_nlse_antigovernor.audit.antigovernor import RolloutConfig, make_rollout_timevarying_closed, make_rollout_timevarying_export, anti_governor_violation


def test_closed_norm_is_reasonably_stable():
    # This test is not asserting determinism; it's asserting "no catastrophic leak".
    # Receipts enforce determinism via quantization; dynamics stay alive.
    n0 = n1 = 64
    T = 128
    params = SchrodParams(hbar_drift=1.0, m_myth=1.0, dx=1.0, dt=0.01)
    cfg = RolloutConfig(V_future_proxy="norm", V_eps=1e-10, tau_eps=1e-10, dealias_frac=0.75)
    rollout = make_rollout_timevarying_closed(n0, n1, params, cfg)

    psi0 = (jnp.ones((n0, n1), dtype=jnp.complex64) + 0.0j) * 0.01
    V_seq = jnp.zeros((T, n0, n1), dtype=jnp.float32)

    psi_T, norms, V_prev, V_curr, dV, tau_export, violations = rollout(psi0, V_seq, coherence_scale=+1.0)

    n0_val = float(conserved_norm(psi0, params.dx))
    nT_val = float(norms[-1])

    # Loose bound: should not drift wildly over short horizon.
    assert abs(nT_val - n0_val) < 1e-3
    # In closed, if we see violations, it's a signal of numeric issues. For this mild regime, expect none.
    assert int(jnp.sum(violations)) == 0


def test_antigovernor_flags_illegitimate_closure():
    V_prev = jnp.array(1.0)
    V_curr = jnp.array(0.5)  # shrink
    tau_export = jnp.array(0.0)  # no export
    dV, viol = anti_governor_violation(V_prev, V_curr, tau_export, V_eps=1e-6, tau_eps=1e-6)
    assert bool(viol) is True

def test_export_channel_prevents_false_violation():
    n0 = n1 = 64
    T = 64
    params = SchrodParams(hbar_drift=1.0, m_myth=1.0, dx=1.0, dt=0.01)

    # Strong boundary absorber will reduce norm, but tau_export should explain it.
    cfg = RolloutConfig(V_future_proxy="norm", V_eps=1e-8, tau_eps=1e-8, dealias_frac=0.75,
                       export_mode="boundary_absorber", boundary_edge_width_frac=0.2, boundary_strength=5.0)
    rollout = make_rollout_timevarying_export(n0, n1, params, cfg)

    psi0 = (jnp.ones((n0, n1), dtype=jnp.complex64) + 0.0j) * 0.01
    V_seq = jnp.zeros((T, n0, n1), dtype=jnp.float32)

    psi_T, norms, V_prev, V_curr, dV, tau_export, violations = rollout(psi0, V_seq, coherence_scale=+1.0)

    assert float(jnp.sum(tau_export)) > 0.0
    # Even though V shrinks, the export explains it => no illegitimate closure.
    assert int(jnp.sum(violations)) == 0
