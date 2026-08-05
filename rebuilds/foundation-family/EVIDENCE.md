<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Rebuild Evidence

**Verification date:** 2026-08-05
**Verified aperture:** one bounded foundation-family transition and finite rollouts; not a claim of full BLOOMCORE organism physiology.

## Custody

- Eight body-linked ZIPs from seven releases are preserved in `original_sources/`.
- Total preserved size: 272,681 bytes.
- All eight files were rehashed against `CUSTODY_MANIFEST.sha256.json` with zero mismatches.
- The custody verifier also opened all 244 ZIP members, checked CRCs, and found no absolute, drive-qualified, or parent-traversal member paths.
- All archives opened and were expanded to `ancestor/<attachment-id>/`. The exact ZIP bytes, not the expanded trees, remain authoritative.
- Extraction-time `__pycache__`, `.pytest_cache`, `.pyc`, and `.DS_Store` artifacts were excluded from the review tree.

## Historical execution

| Surface | Result |
|---|---|
| BLOOMFORCE tests | 3 passed |
| CPU Toy tests | 1 passed |
| Sentinel LITE kernel tests | 1 passed |
| WISECORE GPU smoke | inherited failure: `wisecore_jax.py` imports absent `wuwei_median_Hdot` |
| PDE Engine GPU smoke | inherited failure: `BloomState` dataclass is not a registered JAX pytree for `lax.scan` under JAX 0.9.2 |

Historical payloads were not edited to hide these defects. Repairs live only in the descendant: the WISECORE-style median gate uses `jnp.median`, and JAX state is a `NamedTuple` pytree.

## Descendant proof matrix

| Property | Proof |
|---|---|
| ancestral behavior | shared NumPy oracle transition |
| one-step JAX parity | NumPy and JAX state/metrics compared at float32 tolerance |
| rollout parity | five-step deterministic NumPy/JAX rollout comparison |
| explicit stochasticity | JAX PRNG key carried in state and split at every step |
| replay | equal keys produce byte-equal stochastic fields |
| divergence | different keys produce different stochastic fields |
| zero-extension recovery | uncoupled appended dimensions preserve the base transition |
| causal topology | topology is carried unchanged and base adjacency survives extension |
| receipt custody | deterministic SHA-256 chain verifies independently of transition authority |
| inherited reachability | BLOOMFORCE, CPU Toy, Sentinel kernel, Continuity Spine, and World Engine surfaces imported and exercised |
| Full Fire device | test asserts JAX default backend and first device platform are `gpu` |

Results:

- Windows NumPy/oracle lane: **6 passed, 1 JAX module skipped**; two inherited `datetime.utcnow()` deprecation warnings from World Engine.
- WSL Full Fire lane: **10 passed** on GPU; the same two inherited World Engine deprecation warnings.
- Oracle CLI: receipt chain verified.
- JAX CLI: receipt chain verified and reported `jax=0.9.2`, `platform=gpu`, `devices=[cuda:0]`.
- An isolated PEP 517 build produced both sdist and wheel from the sdist. The wheel was installed into a fresh Windows virtual environment and its console entry point completed with a verified receipt chain.

Build witnesses (artifacts are generated outside the repository and are not custody sources):

| Artifact | SHA-256 |
|---|---|
| `bloomcore_foundation_fire-0.1.0-py3-none-any.whl` | `62d5ebc78013333c3695fd761f586947a12bd82c0ce004102b5dc10ebd8d152a` |
| `bloomcore_foundation_fire-0.1.0.tar.gz` | `7f169e056da46d7dc2adc7f43acc0533438c7fce2662d608fa8738e342857afa` |

## Full Fire environment

The verified environment is a dedicated WSL virtual environment with JAX 0.9.2, jaxlib 0.9.2, CUDA 13 plugin wheels, and an NVIDIA GeForce RTX 4050 Laptop GPU exposed as `cuda:0`.

`scripts/probe_full_fire.py` returned:

```json
{
  "autodiff_finite": true,
  "backend": "gpu",
  "devices": [{"description": "cuda:0", "id": 0, "platform": "gpu"}],
  "jax": "0.9.2",
  "jaxlib": "0.9.2",
  "jit_fft_finite": true,
  "prng_implementation": "threefry2x32",
  "x64_enabled": false
}
```

The CUDA runtime also emitted a non-fatal kernel-driver version parsing warning. JIT FFT, autodiff, the CLI, and all tests still completed successfully on the GPU. This warning is disclosed rather than treated as proof of failure or silently omitted.

## Evidence boundary

This rebuild proves a runnable and parity-checked foundation-family descendant. It does not prove organism-wide Phase 38 coupling, federation, self-modification, canonical promotion of proposed names, or integration of later release families. Receipts witness executions; they do not confer authority.
