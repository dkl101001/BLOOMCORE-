<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Identity and Governance Rebuild Evidence

**Verification date:** 2026-08-27

**Verified aperture:** exact custody for eight releases and 11 attachment records; safe historical entrypoint reachability; one new bounded expression-audit transition; JAX parity for five shared numerical outputs. This is not evidence of complete BLOOMCORE physiology or organism-wide governance.

## Custody

- 11 attachment ZIP records from eight exact, case-sensitive tags are preserved in `original_sources/`.
- Total preserved size: 1,154,362 bytes.
- Eight unique SHA-256 values are present; the two Da Vinci records and three RSS code records remain separate attachment identities despite byte equality.
- `scripts/verify_custody.py` rehashed all bytes, checked all 622 ZIP members by CRC, and found no absolute, drive-qualified, or parent-traversal paths.
- Review expansions contain 350 meaningful files totaling 1,451,392 bytes. Extraction omitted 155 cache/bytecode members. Exact ZIPs, not expansions, remain authoritative.
- Live GitHub release titles, tags, timestamps, bodies, and attachment URLs matched the earlier census immediately before preservation.

## Historical execution

| Surface | Result |
|---|---|
| AetherLoom release verifier | `VERIFY OK (16 files)` |
| Da Vinci attachment `24736682` import test | 1 passed; no broker, network, order, or live-execution call |
| RSS attachment `24869616` tests | 3 passed; duplicate code attachments were hash-proven rather than redundantly promoted |
| Veil-Breath | pressure/re-anchor entrypoint reached in lineage bridge |
| ROK | conservative decision policy reached directly; executor deliberately not invoked |
| Sophia + Compassion | eight-step NumPy reference run completed; 19-receipt hash chain verified |
| NLSE Anti-Governor | 2 passed and 2 inherited failures on JAX 0.9.2 GPU |

The two NLSE failures are preserved rather than repaired inside the ancestor:

1. `make_splitstep_stepper` references undefined `dealias_mask`.
2. `rgrid_2d` is JIT-decorated while receiving dynamic grid sizes, causing a JAX 0.9.2 `ConcretizationTypeError` in the export rollout.

The smaller historical `anti_governor_violation` predicate executes successfully on the GPU and is the only NLSE code path treated as reachable by the descendant proof.

## Descendant proof matrix

| Property | Proof |
|---|---|
| bounded decisions | admit, defer/re-anchor, risk veto, truth failure, and anti-closure cases tested |
| no executable permission | result contract fixes `permissions=non_executable` and `authority=NONE` |
| metric non-authority | maximal trace quality cannot override a false truth signal |
| receipt boundary | receipt chain is appended post-evaluation and independently verifies |
| safe lineage reachability | AetherLoom, Da Vinci governance, Veil-Breath, RSS, ROK, Sophia, and NLSE predicate are directly exercised |
| historical execution exclusion | no Da Vinci broker/executor and no ROK executor imported by the descendant |
| JAX parity | pressure, wisdom score, wisdom gate, anti-closure, and risk veto match Python/NumPy at float32 tolerance |
| packaged governance declaration | installed package exposes the exact Phase 38 source hash and all authority exclusions |

Results:

- Windows reference lane: **15 passed, 1 JAX-module skip**.
- WSL Full Fire-capability lane: **17 passed** on JAX/JAXlib 0.9.2 at `cuda:0`.
- GPU probe: finite JIT audit, `backend=gpu`, device `cuda:0`.
- Isolated PEP 517 source archive and wheel build: passed; fresh-environment wheel install and console entrypoint: passed.

The CUDA runtime emitted the same non-fatal kernel-mode driver-version parsing warning observed in the foundation family. The JIT audit, device execution, and tests completed successfully, so the warning is retained as evidence residue rather than hidden or treated as a failure.

## Artifact witnesses

Build artifacts are generated outside the repository and are not custody sources.

| Artifact | SHA-256 |
|---|---|
| `bloomcore_governance_weave-0.1.0-py3-none-any.whl` | `96939223106108f27ae2cf3b919b4f3a8b51f34a61e4f4a8675094259d7978e9` |
| `bloomcore_governance_weave-0.1.0.tar.gz` | `37a453d438ec8215ef83cb39072c2233aced13e2ea86d86ebc55dfded9abd443` |

## Evidence boundary

This proves a runnable, packaged, model-zero expression-audit composite and exact release-family custody. It does not prove historical whole-transition parity, complete SSFM execution, empirical truth, identity correctness, canonical promotion, market authority, native organism memory, MANTIS/MIRRORSEED completion, Keystone/DSK implementation, causal topology, or organism-wide integration.
