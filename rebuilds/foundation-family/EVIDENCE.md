<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Rebuild Evidence

**Verification dates:** 2026-08-05 initial capture; 2026-08-26 review repair; 2026-08-27 Phase 38 v1.10 reconciliation
**Verified aperture:** one bounded foundation-family transition and finite rollouts; not a claim of full BLOOMCORE organism physiology.

## Phase 38 v1.10 governance binding

The bounded review is bound to active Phase 38 v1.10 SHA-256 `ff058db5dd35fee55168494b17a642fa6ef94bea26e24a5988f07ab80c76de29` and promotion-receipt SHA-256 `9d1739c59e8ff5689258399afc31d616a34508e6c74e0d22d86106a258b12e70`. The complete execution membrane and complete Section 33 governed the pass. See `PHASE38_V1_10_REVIEW.md` for the source-binding ledger and bounded requirement dispositions.

Keystone v1.3 is recognized as optional governed noncanonical research but remains outside this PR's accepted implementation aperture. This build therefore makes no source-faithful Keystone or DSK claim.

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
| source mapping | exact archive hashes and surviving entrypoints mapped in the descendant README; the new composite is not labeled an ancestral oracle |
| packaged v1.10 contract | machine-readable declaration supplies every Section 33.8 field and is verified from installed package resources |
| one-step JAX parity | every shared NumPy/JAX state field and every metric/gate output compared at float32 tolerance |
| rollout parity | five-step deterministic comparison of every shared final-state field and every metric/gate series |
| explicit stochasticity | JAX PRNG key carried in state and split at every step |
| replay | equal keys produce byte-equal stochastic fields |
| divergence | different keys produce different stochastic fields |
| zero-extension recovery | five-step NumPy and JAX tests show uncoupled appended dimensions preserve shared state, energy history, metrics, and gate outputs |
| topology payload boundary | topology is carried unchanged and base adjacency survives extension; tests and documentation explicitly show it is not yet causal input |
| receipt custody | deterministic SHA-256 chain verifies independently of transition authority |
| inherited reachability | BLOOMFORCE, CPU Toy, Sentinel kernel, Continuity Spine, and World Engine surfaces imported and exercised without claiming whole-transition equivalence |
| Full Fire device | test asserts JAX default backend and first device platform are `gpu` |

Results:

- Windows NumPy/reference lane: **8 passed, 1 JAX module skipped**; two inherited `datetime.utcnow()` deprecation warnings from World Engine.
- WSL Full Fire-capability lane: **12 passed** on GPU; the same two inherited World Engine deprecation warnings.
- Oracle CLI: receipt chain verified.
- JAX CLI: receipt chain verified and reported `jax=0.9.2`, `platform=gpu`, `devices=[cuda:0]`.
- An isolated PEP 517 build produced both sdist and wheel from the sdist. The wheel was installed into a fresh Python 3.13 Windows virtual environment; the packaged v1.10 contract was loaded and hash-checked through `importlib.resources`, and the console entry point completed with a verified receipt chain.

Build witnesses (artifacts are generated outside the repository and are not custody sources):

| Artifact | SHA-256 |
|---|---|
| `bloomcore_foundation_fire-0.1.0-py3-none-any.whl` | `6ecab182bcc1d3f702de140870b6616b7a63f4fb03491b2e35fcfacaa8d9c6cb` |
| `bloomcore_foundation_fire-0.1.0.tar.gz` | `4e31a60092249f8fcabec906039f05b1c3c3e9fd5bb1a0ba9c270c6c1e80896f` |

## Full Fire environment

The verified environment remains installed at `~/.venvs/bloomcore-full-fire-jax-0.9.2`. It contains JAX 0.9.2, jaxlib 0.9.2, `jax-cuda13-plugin` 0.9.2, `jax-cuda13-pjrt` 0.9.2, and pytest 9.1.1. WSL exposes the NVIDIA GeForce RTX 4050 Laptop GPU as `cuda:0` through the Windows driver.

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

## Validation scope

`git diff --check` passes for the authored descendant, custody, and navigation surfaces. A whole-branch invocation also inspects byte-preserved ancestor expansions and reports their historical trailing spaces and blank final lines. Those bytes match the authoritative ZIPs and are intentionally not rewritten; the preservation exception is disclosed instead of claiming an unqualified whole-branch pass.

## Evidence boundary

This rebuild proves a runnable and parity-checked new foundation-family composite with a packaged bounded Phase 38 v1.10 execution declaration. It does not prove ancestral whole-transition equivalence, causal use of the topology payload, organism-wide Phase 38 coupling, federation, self-modification, Keystone/DSK implementation, canonical promotion of proposed names, or integration of later release families. Receipts witness executions; they do not confer authority.
