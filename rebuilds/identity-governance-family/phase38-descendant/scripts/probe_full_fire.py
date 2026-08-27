# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json


def main() -> int:
    import jax
    import jax.numpy as jnp

    from bloomcore_governance_weave.jax_backend import jitted_jax_audit

    values = jnp.asarray(
        [0.82, 0.18, 0.20, 0.91, 0.92, 0.90, 0.86, -0.03, 0.08, 0.07, 0.09, 0.10, 0.08, 0.12, 1.0, 1.0, 0.0],
        dtype=jnp.float32,
    )
    out = jitted_jax_audit(values)
    out.block_until_ready()
    payload = {
        "jax": jax.__version__,
        "backend": jax.default_backend(),
        "devices": [str(device) for device in jax.devices()],
        "audit_finite": bool(jnp.all(jnp.isfinite(out))),
        "audit": [float(value) for value in out],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["audit_finite"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
