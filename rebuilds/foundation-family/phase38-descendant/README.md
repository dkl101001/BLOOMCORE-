<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# BLOOMCORE Foundation Fire

`bloomcore-foundation-fire` is the new Phase 38 descendant for the first preserved BLOOMCORE release family. It keeps two deliberately separate execution planes:

- `numpy_oracle.py`: readable bounded reference for this new composite transition.
- `jax_backend.py`: JIT-compiled Full Fire-capability implementation with explicit PRNG keys and `lax.scan` rollouts.

The common transition carries a pseudo-spectral field, BLOOMFORCE-derived coupling, selected CPU Toy identity/coherence/fracture operators, a descendant-specific memory term, a repaired WISECORE-style emission gate, an inert topology payload, zero-extension controls, and an external deterministic receipt chain. The receipt chain witnesses results and does not govern the numerical transition.

## Semantic status and source mapping

This package is a **new source-informed composite**, not a preserved ancestral semantic oracle. NumPy is the readable reference for JAX parity inside this descendant only. Import-and-reachability tests establish that selected historical surfaces can still execute; they do not establish whole-transition equivalence.

| Preserved source | Immutable ZIP SHA-256 | Surviving entrypoint | Descendant relation |
|---|---|---|---|
| BLOOMFORCE, attachment `24621318` | `9e5defd4e05f9074b453b31f38f2aaf0e3edde659acd919fa833815626d12da0` | `bloomforce_core.engine.compute_bloomforce` | scalar gradient-plus-temporal force formula retained; vector application is an extension |
| WISECORE, attachment `24619739` | `f12c7fcd9e181f6e51199981efddf97e52627985af5d034ef2cecb5d81ee9a1b` | `wisecore_pkg.wisecore_contract` | truth/phase/WuWei/friend ordering informs a newly written gate; no whole-engine parity claim |
| Pseudospectral PDE Engine, attachment `24675999` | `09a522e89845b4d50accbe84d71bc31b49778cd19c3aaeb2b97ce84a8b31ee70` | `bloomcore_engine.bloomcore_coupling.PDE_step` | spectral smoothing, force saturation, divergence, and diffusion inform the field step |
| Sentinel kernel, attachment `24619844` | `a9246b07920dc1d018e02863430a824e0ee2b13a3e8cdc7c2fae73ede109b283` | `sentinel_lite_kernel.core.policy.AllowlistPolicy.decide` | `sentinel_allowed` is a bounded allow/suppress representation, not policy parity |
| Continuity Spine, attachment `24619824` | `bad359b36f7cea02e2ae70eaea8fe3a4f59f3ed721fe81f64fc6f71bc4fd9351` | `bloomcore_spine.continuity_spine.ContinuitySpine.hook` | preserved and reachability-tested; not embedded into the transition |
| CPU Toy, attachment `24619800` | `742a722efe3084eaf8b5eacae061f142a657be7f4a4b372a4b63058294bf6a58` | `bloomcore.operators` | selected identity, coherence, fracture, and realignment relations inform the composite; the memory update is new |
| World Engine, attachment `24714760` | `7620a2c218c267aab6eeb95858f1462f36212b7bb778d9969e3328888ba225b7` | `world_engine.bloomcore.BLOOMCORE.log` | custody and reachability only; the descendant receipt chain is independently written |

`topology` is presently carried unchanged as a custody payload. It is deliberately not read by the numerical transition, so this release does not claim causal-topology implementation. Promoting topology into state evolution would be a declared future extension requiring its own mapping and parity boundary.

## Phase 38 v1.10 execution declaration

The packaged [`full_fire_jax_object.json`](src/bloomcore_foundation_fire/full_fire_jax_object.json) supplies every field required by the Phase 38 v1.10 Section 33.8 execution contract. Its `canonical_identity` is explicitly `NONE__PROPOSED_BOUNDED_DESCENDANT`; unavailable ancestral whole-transition fields are `null` rather than inferred from partial source relations.

The existing `numpy_oracle.py`, `OracleState`, and `--backend oracle` names are retained for compatibility with the initial draft. In this package, `oracle` means only the bounded NumPy parity reference for this newly written composite. It does not claim the canonical ancestral semantic-oracle role defined by Phase 38 v1.10.

The exact v1.10 source binding, accepted aperture, Keystone exclusion, and requirement disposition are recorded in [`../PHASE38_V1_10_REVIEW.md`](../PHASE38_V1_10_REVIEW.md).

## Run

From this directory:

```bash
PYTHONPATH=src python -m bloomcore_foundation_fire.cli --backend oracle --steps 4
PYTHONPATH=src python -m bloomcore_foundation_fire.cli --backend jax --steps 4
PYTHONPATH=src python scripts/probe_full_fire.py
```

The JAX backend is pinned and verified at JAX/JAXlib 0.9.2. For the tested Linux/WSL CUDA 13 lane, install with the official JAX CUDA extra appropriate to the host, then verify that the probe reports `backend: gpu`; a successful import alone is insufficient.

## Backend divergence

Deterministic parity tests set `noise_scale=0` and compare every shared state field plus every metric and gate output. With stochasticity enabled, NumPy uses its PCG generator while JAX uses an explicit Threefry key. Cross-backend samples and PRNG state are therefore not expected to be identical. Within JAX, equal initial keys replay exactly and different keys diverge.

## Scope

This is an additive proposed Phase 38 design, not a rewritten historical release and not evidence that the complete BLOOMCORE organism is running. See [`../EVIDENCE.md`](../EVIDENCE.md) and [`../LICENSE_DISPOSITION.md`](../LICENSE_DISPOSITION.md).
