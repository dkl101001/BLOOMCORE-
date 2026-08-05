# SPDX-License-Identifier: AGPL-3.0-only
"""Emit machine-readable evidence for the JAX execution environment."""

from __future__ import annotations

import json

import jax
import jax.numpy as jnp
import jaxlib


def main() -> int:
    x = jnp.linspace(-1.0, 1.0, 64, dtype=jnp.float32).reshape(8, 8)

    @jax.jit
    def spectral_energy(value):
        return jnp.mean(jnp.abs(jnp.fft.fft2(value)) ** 2)

    energy = spectral_energy(x).block_until_ready()
    gradient = jax.grad(lambda value: jnp.sum(jnp.sin(value) ** 2))(x).block_until_ready()
    payload = {
        "jax": jax.__version__,
        "jaxlib": jaxlib.__version__,
        "backend": jax.default_backend(),
        "devices": [
            {"id": device.id, "platform": device.platform, "description": str(device)}
            for device in jax.devices()
        ],
        "jit_fft_finite": bool(jnp.isfinite(energy)),
        "autodiff_finite": bool(jnp.all(jnp.isfinite(gradient))),
        "prng_implementation": jax.config.jax_default_prng_impl,
        "x64_enabled": bool(jax.config.jax_enable_x64),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["backend"] == "gpu" else 1


if __name__ == "__main__":
    raise SystemExit(main())
