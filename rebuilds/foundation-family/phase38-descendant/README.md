<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# BLOOMCORE Foundation Fire

`bloomcore-foundation-fire` is the new Phase 38 descendant for the first preserved BLOOMCORE release family. It keeps two deliberately separate execution planes:

- `numpy_oracle.py`: readable ancestral-Python semantic oracle.
- `jax_backend.py`: JIT-compiled Full Fire implementation with explicit PRNG keys and `lax.scan` rollouts.

The common transition carries the pseudo-spectral field, BLOOMFORCE coupling, CPU Toy identity/coherence/fracture/memory terms, a repaired WISECORE-style emission gate, causal topology, zero-extension controls, and an external deterministic receipt chain. The receipt chain witnesses results and does not govern the numerical transition.

## Run

From this directory:

```bash
PYTHONPATH=src python -m bloomcore_foundation_fire.cli --backend oracle --steps 4
PYTHONPATH=src python -m bloomcore_foundation_fire.cli --backend jax --steps 4
PYTHONPATH=src python scripts/probe_full_fire.py
```

The JAX backend is pinned and verified at JAX/JAXlib 0.9.2. For the tested Linux/WSL CUDA 13 lane, install with the official JAX CUDA extra appropriate to the host, then verify that the probe reports `backend: gpu`; a successful import alone is insufficient.

## Backend divergence

Deterministic parity tests set `noise_scale=0`. With stochasticity enabled, NumPy uses its PCG generator while JAX uses an explicit Threefry key. Cross-backend samples are therefore not expected to be identical. Within JAX, equal initial keys replay exactly and different keys diverge.

## Scope

This is an additive proposed Phase 38 design, not a rewritten historical release and not evidence that the complete BLOOMCORE organism is running. See [`../EVIDENCE.md`](../EVIDENCE.md) and [`../LICENSE_DISPOSITION.md`](../LICENSE_DISPOSITION.md).
