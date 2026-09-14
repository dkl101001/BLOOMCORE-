<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Hybrid reference revision — 2026-09-14

## Merge-review follow-up: median overflow

Review of `e562d5d418e50ae383394d2ec8fafaa772fd4280` found that the median of finite `(-1e308, -1e308)` became negative infinity without entering the derived-value validity check. The audit admitted the simulation with empty residue. The current correction calculates that intermediate once, checks finiteness before the wisdom comparison, and includes it in the numeric-residue check. Positive and negative median overflow are now suppressed and witnessed; a large finite nonoverflowing median remains valid.

Fresh rerun after correction: **32 passed, 1 JAX skip on Windows; 34 passed on WSL JAX/JAXlib 0.9.2**. GPU probe completed on `cuda:0` with finite output; the previously disclosed driver-version warning remains. These suites include custody and selected historical bridge checks. Both overflow signs are covered in strict-JSON round-trip tests and explicit gate/residue tests, plus a nonoverflow control.

Isolated sdist/wheel rebuild and a fresh installed-wheel negative-median regression passed. New artifacts are retained separately in `outputs/hybrid-median-fix-artifacts/`; initial draft artifacts and the evidence below are preserved. Version 0.2.0 remains an unpublished draft version, distinguished here by exact hashes:

| Corrected artifact | SHA-256 |
|---|---|
| `bloomcore_governance_weave-0.2.0-py3-none-any.whl` | `d3a9abd9e70052af9d359a266b4cbe71773282fb662c3b41addfd1d9c55f755a` |
| `bloomcore_governance_weave-0.2.0.tar.gz` | `f41b0ed47166afff0c13bdb5af83a1fd3ea0e6e6a64c9e6ffc5ecb972b3533d4` |

This addresses the reproduced median-overflow finding; it is not an exhaustive numerical-validity proof or merge authorization. No native scope, source binding, historical ancestor, or licensing change is made.

## Initial revision record (before median correction)

Current local revision: `hybrid-descendant/`, distribution version 0.2.0. Parent: commit `82939aab7ed3141cbe68f56c6d689515fc07dfea`, `phase38-descendant/` version 0.1.0. No parent source, historical archive, extracted ancestor, license, or August review/evidence file was rewritten. A navigation paragraph was added to the family README. Nothing was pushed or merged by this revision.

## Selected source and bounded coverage

The Operator selected `HYBRID_TRIAD_OI_LINEAGE_v0.1_CANONICAL.md` as the current reference. SHA-256: `46f1592d80963c0129a92f134eff9e9136e4a04f6d300fa98494bbbad87e7f2b`, in archive `8cef4677a0095aa1bebff7969979a453fa8a07ba7a7163ad5286e1220864907b`. Its current binding to full Triad master `113ddf6f01849be2f7ec735f1e66d89c57cef174df53f84f8b6ffe0ef87e9e3e` remains intact. Embedded promotion statements do not authorize this tool to promote or publish anything.

The preceding source review read Hybrid lines 1–1135 in full, including activation, portable packaging law, OI patch, K1–K4, execution-selection law and H01–H12; embedded Keystone section 30; the complete implementation map (`b4373f17cf851d34e965aab3897aa0bd5b18ca556a679f24b0c11a03b11e311f`) and Phase 151 binding (`65c09349c2aa84c6a1913c84b95633c68e46b4bbd748e33c8b761febc8a18e51`). This implementation follows that bounded source review and re-read the selected code and tests. It does not claim complete master/Keystone reading, full source consolidation, new scientific evidence, native physiology, or organism-wide conformity.

Canonical sources remain in Operator custody, referenced rather than copied into the public package. Supplied ZIP payload integrity was checked at intake; full external ancestry availability is not established here. The current wheel/sdist are Python distribution artifacts, not a newly promoted portable-lineage release packet. A future release packet still requires its exact payload/dependency manifest and detached ancestry evidence; neither artifact includes nested old releases.

## Review findings addressed

| Finding | Revision and evidence | Remaining boundary |
|---|---|---|
| F1: non-finite failure receipts | v2 results use null unavailable diagnostics and path-classified numeric residue. Empty windows, NaN, both infinities and finite overflow are covered; strict JSON round-trip and deterministic hashes tested. Direct non-finite receipt payloads fail before chain mutation. Payload copies prevent caller aliasing. | Python serialization is not advertised as RFC8785. Malformed types may raise. Receipt chain is single-writer, in-memory, not durable native commitment. |
| F2: stale current binding | New packaged Hybrid source declaration and this successor record; copied old contract explicitly historical only. | Historical source hashes, parent meanings and old validation results remain unchanged. |
| F3: missing execution declarations | Nine public entrypoint profiles resolve eight axes plus precision/equality, failure, scheduling, randomness, resource/cancellation limits and exclusions. CLI metadata includes actual source hashes and environment versions. Tests resolve all declared callables and profile fields. | No hard wall-time/memory quotas or native scheduling isolation implemented. Those absences are declared, not marked complete. Metadata is not proof of every named backend running. |
| F4: model absence versus physiology | `model_calls=false`, `canonical_native_mode=null`, native model-zero operation explicitly `NOT_IMPLEMENTED`. | No new canonical model mode invented; no native learning, memory or reconstruction claimed. |

Finite baseline formulas and legacy simulation status meanings are retained. Invalid arithmetic is newly suppressed in the bounded simulation, with preserved residue rather than an invented healthy diagnostic. The audit still cannot execute candidate text or change native state. Before any native coupling, review the K2 observer boundary and prove audit-on/off noninterference, observer-fault isolation and actual admission semantics. No native MANTIS/MIRRORSEED execution is claimed.

## Fresh validation

- Windows Python 3.13, isolated environment, NumPy 2.5.3 / pytest 9.1.1: **27 passed, 1 skipped**. JAX is intentionally absent in that environment.
- WSL Ubuntu Python 3.12.3, NumPy 2.5.1 / pytest 9.1.1 / JAX and JAXlib 0.9.2: **29 passed**.
- WSL GPU probe: backend `gpu`, device `cuda:0`, finite five-value audit. The kernel-driver version-format warning was emitted and retained; it did not prevent completion.
- Tests include family custody, selected historical bridge entrypoints, original local evaluation checks, finite NumPy/JAX fixture comparison, strict failure receipts and current contract/profile checks. The two full historical NLSE rollout failures reported in August were not rerun or repaired; the small predicate is exercised, not the whole solver.
- Isolated PEP 517 sdist and wheel build succeeded with setuptools 84.0.0 and wheel 0.48.0. The wheel was built from the sdist.
- Clean Windows wheel installation in a separate environment verified installed version/path, packaged Hybrid reference, strict invalid-input receipt and chain verification.
- Installed console entrypoint returned `ADMIT_EXPRESSION`, a verified receipt chain and the `cli:main` execution profile. The direct custody verifier separately checked 11 archives, 1,154,362 bytes, 622 ZIP members and eight unique payload hashes, with zero failures.

These test counts apply to this descendant and its selected bridge/custody tests, not to a complete BLOOMCORE rebuild. One finite fixture does not establish arbitrary threshold equivalence or historical whole-transition parity. The direct historical custody verifier remains an archive integrity check, not license clearance or a native restore demonstration.

## Generated artifact identities

Artifacts remain outside the repository in the local `outputs/hybrid-revision-artifacts/` folder.

| Artifact | SHA-256 |
|---|---|
| `bloomcore_governance_weave-0.2.0-py3-none-any.whl` | `f166dc605babb31072e2478f16484b179904c40af43ac77ea32ea0db9fffaa57` |
| `bloomcore_governance_weave-0.2.0.tar.gz` | `0e450765214ab6ddc404cc5114e08c5f0ebb25e2302c10b16823112f46a2abc6` |

The installed runtime is self-contained with its declared NumPy dependency. Historical bridge/custody tests deliberately require external family sources; they are not represented as independently available inside the wheel/sdist. Family navigation and old-source links in the README assume the repository context.

## Remaining publication work

Review this local diff, then update the draft PR description and push only through the agreed publication sequence. A current portable release manifest, expanded numerical boundary coverage, native integration and resource isolation remain separate work. Public README/FAQ/OI orientation and later release families are not revised by this bounded package pass. NOW and Basics remain untouched lineage.
