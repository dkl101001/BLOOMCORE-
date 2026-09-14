from __future__ import annotations

import json
import jax
import jax.numpy as jnp

from bloomcore_nlse_antigovernor.physics.ssfm import SchrodParams
from bloomcore_nlse_antigovernor.audit.antigovernor import RolloutConfig, make_rollout_timevarying_closed, make_rollout_timevarying_export
from bloomcore_nlse_antigovernor.receipts.build import build_anti_governor_receipts


def main():
    n0 = n1 = 128
    T = 256

    params = SchrodParams(hbar_drift=1.0, m_myth=1.0, dx=1.0, dt=0.01)
    cfg = RolloutConfig(V_future_proxy="norm", V_eps=1e-8, tau_eps=1e-8, dealias_frac=0.75, dealias_power=8)

    rollout = make_rollout_timevarying_closed(n0, n1, params, cfg)

    # Export channel demos (choose one):
    cfg_export_boundary = RolloutConfig(V_future_proxy="norm", V_eps=1e-8, tau_eps=1e-8, dealias_frac=0.75, dealias_power=8,
                                      export_mode="boundary_absorber", boundary_edge_width_frac=0.15, boundary_strength=3.0)
    rollout_export_boundary = make_rollout_timevarying_export(n0, n1, params, cfg_export_boundary)

    cfg_export_radiator = RolloutConfig(V_future_proxy="fft_eff_rank", V_eps=1e-8, tau_eps=1e-8, dealias_frac=0.75, dealias_power=8,
                                      export_mode="highk_radiator", radiator_frac=0.75, radiator_power=8, radiator_strength=1.5)
    rollout_export_radiator = make_rollout_timevarying_export(n0, n1, params, cfg_export_radiator)

    psi0 = (jnp.ones((n0, n1), dtype=jnp.complex64) + 0.0j) * 0.01

    # Simple time-varying potential: a breathing Gaussian bump
    xs = jnp.linspace(-1.0, 1.0, n0)
    X, Y = jnp.meshgrid(xs, xs, indexing="ij")
    gauss = jnp.exp(-(X**2 + Y**2) / (2.0 * 0.2**2)).astype(jnp.float32)

    amp = jnp.sin(jnp.linspace(0.0, 8.0, T)).astype(jnp.float32)
    V_seq = (amp[:, None, None] * gauss[None, :, :]).astype(jnp.float32)

    psi_T, norms, V_prev, V_curr, dV, tau_export, violations = rollout(psi0, V_seq, coherence_scale=-2.0)

    receipts = build_anti_governor_receipts(
        V_prev=[float(x) for x in V_prev.tolist()],
        V_curr=[float(x) for x in V_curr.tolist()],
        dV=[float(x) for x in dV.tolist()],
        tau_export=[float(x) for x in tau_export.tolist()],
        violation=[bool(x) for x in violations.tolist()],
        meta={
            "V_future_proxy": cfg.V_future_proxy,
            "dx": params.dx,
            "dt": params.dt,
            "note": "Receipts hash quantized metrics only; dynamics may vary across backends.",
        },
    )

    out = {
        "norm_first": float(norms[0]),
        "norm_last": float(norms[-1]),
        "violations": int(jnp.sum(violations)),
        "first_receipt_hash": receipts[0]["hash"],
        "export_boundary_tau_sum": float(jnp.sum(tau_b)),
        "export_boundary_violations": int(jnp.sum(viol_b)),
        "export_radiator_tau_sum": float(jnp.sum(tau_r)),
        "export_radiator_violations": int(jnp.sum(viol_r)),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
