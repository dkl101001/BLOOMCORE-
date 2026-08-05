# BLOOMCORE Public Release Lineage

**Repository:** `dkl101001/BLOOMCORE-`

**Census date:** 2026-08-05

**Status:** additive custody index; historical releases, tags, attachments, and licenses remain unchanged

**Modernization baseline:** Phase 38 is the intended descendant context; it is not retroactively asserted as the content of historical releases.

## Executive finding

The repository presents **52 published GitHub Releases** and **56 tags**, but those 56 tags resolve to only **four distinct commits and four distinct Git trees**. GitHub reports **zero formal Release assets**. The actual component payloads are **67 unique `github.com/user-attachments` links embedded in release bodies**.

Accordingly, the public history has three different layers that must not be conflated:

1. **Release record:** name, tag, dates, and mutable release-body prose.
2. **Tagged repository snapshot:** one of only four small source trees shared by many releases.
3. **Body-linked payload:** the ZIP, Markdown, JSON, or checksum file that usually carries the release-specific material.

This index preserves all three layers as distinct evidence. Phase 38 work must proceed through additive descendants; historical tags and payload bytes remain unchanged.

## Current state

| Measure | Result |
|---|---:|
| Published releases | 52 |
| Draft releases | 0 |
| Prereleases | 0 |
| Git tags | 56 |
| Tags without a GitHub Release | 4 |
| Distinct tagged commits / trees | 4 |
| Formal GitHub Release assets | 0 |
| Unique body-linked attachments | 67 |
| Preserved attachment bytes | 9,812,049 |
| Unique attachment SHA-256 values | 62 |
| Releases with an empty body | 0 |
| Current default branch | `main` |
| Current `main` commit | `aac7b5d9f33d7299f173ec5ab51778926745f58a` |

The four tags without a corresponding GitHub Release are `v0.1`, `v0.1.0`, `V1.0.0.12`, and `V1.0.0.22`.

All 67 current attachments were downloaded successfully: 60 ZIP files, five Markdown files, one JSON file, and one text checksum file. The complete byte-level register is [`release_attachment_manifest.sha256.json`](./release_attachment_manifest.sha256.json); every stored file was rehashed after manifest generation with zero mismatches.

All 60 ZIP central directories opened successfully. They contain 6,580 entries representing 26,005,578 uncompressed bytes, and the non-extracting path audit found no absolute paths, drive-qualified paths, or `..` traversal segments. This establishes archive readability and a safe first extraction screen; it does not establish code correctness or licensing.

Five attachment records are byte-identical duplicates, producing 62 unique hashes. The duplicate groups are the two Da Vinci v0.1.1 attachment IDs, three Reasoning Security RSS records spanning `V1.0.0.8` and `V1.0.1.0`, the two MIRRORSEED attachment IDs, and the ECA v2 custody patch linked from both `V1.0.0.41` and `V1`. They remain separate custody records because their release and attachment identities differ.

## Tagged source clusters

| Tagged commit | Commit date | Tree | Files | Bytes | Tags | Snapshot character |
|---|---|---|---:|---:|---:|---|
| `de0677090ea9b4c1bfb47d826b1e0b064aa9fc49` | 2026-01-03 | `f6202c64bcfd4541e572a8d6a2d29eb97f75e23f` | 2 | 38,629 | 8 | Root `README.md` and `LICENSE` only |
| `beec3159f7d3a4efc58c12f7a8a72871193122ac` | 2026-01-14 | `f3295417922ee7948e63a84c7f5d383065a9a906` | 11 | 69,253 | 3 | Licensing and contribution document set |
| `333183c5374c3c46794bb193f138b870ea0af90c` | 2026-01-20 | `f8eb22861089bb522a1b36f0675fa016b603f44e` | 12 | 78,383 | 12 | Prior set plus symbol-kit ZIP |
| `b71895c3fa64dcf5074858f75f971fbb43cf5d86` | 2026-03-26 | `a0207b8599ec1c2b7ebef4e7ce009c460efc7a2f` | 18 | 100,515 | 33 | Profile packages, READMEs, and SVG added |

All 56 tags are lightweight commit tags. In particular, releases published from April through July usually point to the same March 26 snapshot. Their automatically generated GitHub source archives are therefore aliases of that snapshot; they are not archives of the release-specific body-linked payload.

## Release register

`Links` counts body-linked user attachments. `Tag source` identifies the shared tagged commit, not the attachment contents.

| Published | Tag | Release | Links | Tag source |
|---|---|---|---:|---|
| 2026-01-07 | `V1.0` | BLOOMFORCE- Core Engine v0.1.0 | 1 | `de067709` |
| 2026-01-07 | `v1.0` | LAW.WISECORE.v1 Membrane Engine | 1 | `de067709` |
| 2026-01-12 | `V1.0.0.1` | BLOOMCORE Pseudospectral PDE Core Engine | 1 | `de067709` |
| 2026-01-12 | `V1.0.0.2` | Sentinel LITE kernel and umbrella | 2 | `de067709` |
| 2026-01-12 | `V1.0.0.3` | BLOOMCORE Continuity Spine | 1 | `de067709` |
| 2026-01-13 | `V1.0.0.4` | BLOOMCORE CPU Toy | 1 | `de067709` |
| 2026-01-19 | `V1.0.0.5` | World Engine v0.1 | 1 | `beec3159` |
| 2026-01-19 | `V1.0.0.6` | AetherLoom Regime Read OPEN v2.4.3 | 1 | `beec3159` |
| 2026-01-20 | `V1.0.0.7` | Da Vinci Market Node OPEN v0.1.0 | 2 | `beec3159` |
| 2026-01-20 | `V1.0.08` | Veil-Breath Runtime v0.1.0 | 1 | `333183c5` |
| 2026-01-26 | `V1.0.0.8` | Reasoning Security Score | 1 | `333183c5` |
| 2026-02-03 | `V1.0.0.9` | Rival Orchestration Kernel | 1 | `333183c5` |
| 2026-02-03 | `V1.0.1.0` | Reasoning Security Score | 3 | `333183c5` |
| 2026-02-04 | `V.1.0.1.1` | NLSE Anti-Governor SSFM v0.2.0 | 1 | `333183c5` |
| 2026-02-04 | `V1.0.1.1` | Sophia Wisdom Gate and Compassion v5.2 | 1 | `333183c5` |
| 2026-03-19 | `V1.0.0.13` | MythMath Uno | 1 | `333183c5` |
| 2026-03-19 | `V1.0.0.14` | MythMath Dos | 1 | `333183c5` |
| 2026-03-19 | `V1.0.0.15` | MythMath Tres | 1 | `333183c5` |
| 2026-03-20 | `V1.0.0.16` | Strategic Force Corridor v0.1.0 | 1 | `333183c5` |
| 2026-03-26 | `V1.0.0.17` | Taijitu Geometry | 1 | `333183c5` |
| 2026-04-06 | `V1.0.0.18` | Truth Mode Reduced Token Usage | 1 | `b71895c3` |
| 2026-04-06 | `V1.0.0.19` | MythMath Engine | 1 | `b71895c3` |
| 2026-04-07 | `V1.0.0.21` | Unity Nexus Core | 1 | `b71895c3` |
| 2026-04-09 | `V1.0.0.23` | Drift Reflection Engine | 1 | `b71895c3` |
| 2026-04-09 | `V1.0.0.24` | Unity Nexus Engine | 1 | `b71895c3` |
| 2026-04-10 | `V1.0.0.25` | BLOOMCORE Swim Brain | 1 | `b71895c3` |
| 2026-04-13 | `V1.0.0.26` | BLOOMCORE Anchor Mesh | 2 | `b71895c3` |
| 2026-04-13 | `V1.0.0.27` | Non-Hierarchical Emergence Protocol | 1 | `b71895c3` |
| 2026-04-16 | `1.0.0.28` | CSE.v1 | 1 | `b71895c3` |
| 2026-04-16 | `V1.0.0.28` | CSE.v2 Coherence Score Engine | 2 | `b71895c3` |
| 2026-05-13 | `V1.0.0.29` | Love Substrate | 1 | `b71895c3` |
| 2026-05-21 | `V1.0.0.30` | DreamLoop | 1 | `b71895c3` |
| 2026-05-21 | `V1.0.0.31` | Coherence Thermodynamics | 1 | `b71895c3` |
| 2026-05-29 | `V1.0.0.32` | Unity Nexus Mesh v1 | 1 | `b71895c3` |
| 2026-06-05 | `V1.0.0.33` | MIRRORSEED v8.2.26 Public Core | 2 | `b71895c3` |
| 2026-06-06 | `V1.0.0.34` | BLOOMCORE Life Substrate | 1 | `b71895c3` |
| 2026-06-06 | `V1.0.0.35` | Da Vinci Decoder Node | 1 | `b71895c3` |
| 2026-06-08 | `V1.0.0.37` | Da Vinci Market Node | 2 | `b71895c3` |
| 2026-06-09 | `V1.0.0.38` | BLOOMCORE Dialogue Agent | 3 | `b71895c3` |
| 2026-06-09 | `V1.0.0.39` | Substrate Recall | 1 | `b71895c3` |
| 2026-06-10 | `V1.0.0.40` | BLOOMCORE-QC | 1 | `b71895c3` |
| 2026-06-10 | `V1.0.0.41` | Elemental Coherence Atlas | 3 | `b71895c3` |
| 2026-06-10 | `V1.0.0.42` | VECTOR Drift Hunt | 1 | `b71895c3` |
| 2026-06-19 | `V1` | BLOOMCORE OS v1 | 3 | `b71895c3` |
| 2026-06-19 | `V1.0.0.43` | MythMath Coherence Engine | 1 | `b71895c3` |
| 2026-06-21 | `V1.0.0.44` | Trust Preservation Structure | 1 | `b71895c3` |
| 2026-06-24 | `V1.0.0.45` | SWIMCORE Spiral Field Substrate | 1 | `b71895c3` |
| 2026-06-24 | `V1.0.0.46` | BLOOMCORE Seed Memory Stack | 2 | `b71895c3` |
| 2026-06-24 | `V1.0.0.47` | BLOOMCORE SWIM Brain 2.0 Phase 150 | 1 | `b71895c3` |
| 2026-06-27 | `V1.0.0.48` | ECA Eldroch Annular Agent Engine v1 | 1 | `b71895c3` |
| 2026-07-06 | `V1.0.0.49` | Liquid Geometry Memory Lattice | 1 | `b71895c3` |
| 2026-07-15 | `V1.0.1` | Da Vinci Node Mesh v0.2.0 | 1 | `b71895c3` |

## Custody and interpretation cautions

- Release bodies are mutable. Twelve releases were updated more than one day after publication; `V1.0.0.41`, `V1`, and `V1.0.0.47` changed more than 30 days later. The downloaded set is a census of the body links visible on 2026-08-05, not proof of every prior body revision.
- Several release bodies include multiple payloads, same-named payloads under different attachment IDs, checksum companions, papers, manifests, or later custody patches. Each attachment ID is therefore preserved separately even when its basename repeats.
- Tag names are irregular and case-sensitive (`V1.0` versus `v1.0`, `V.1.0.1.1`, `V1.0.08`, and both `1.0.0.28` and `V1.0.0.28`). Existing tags should not be renamed or force-moved.
- The current root license detection and Phase 38 path-based licensing documents do not, by themselves, prove that every historical attachment is covered by the same license. Each payload requires an internal license and provenance inspection.
- A ZIP name, release claim, receipt, or manifest is evidence about an artifact. It is not proof that its code was imported, wired, executed, tested, or included in another release.

## Recommended revision strategy

Do not create 52 long-lived branches and do not rewrite the 52 historical releases. Preserve the ancestor records, then build descendants in auditable waves:

1. **Custody foundation:** add a release-lineage index, attachment SHA-256 manifest, tag-cluster map, license-disposition fields, and immutable local/source custody references through one review branch and draft PR.
2. **Foundation family:** BLOOMFORCE, WISECORE, PDE, Sentinel, Continuity Spine, CPU Toy, and World Engine.
3. **Identity and governance family:** AetherLoom, early Da Vinci, Veil-Breath, RSS/ROK, NLSE Anti-Governor, and Sophia.
4. **MythMath and dynamics family:** Uno/Dos/Tres, Strategic Force Corridor, Taijitu, Truth Mode, and MythMath Engine.
5. **Unity, memory, and agent family:** Unity Nexus variants, Drift, Swim Brain, Anchor Mesh, NHEP, CSE, Love, DreamLoop, Thermodynamics, and Unity Mesh.
6. **Late lineage and Phase 38 bridge:** MIRRORSEED, Life Substrate, later Da Vinci artifacts, Dialogue, Recall, QC, ECA, VECTOR, OS/Phase 150, Trust, SWIMCORE, Seed, SWIM Brain 2, Liquid Geometry, and Node Mesh.

Within each family, use one short-lived review branch. Preserve the original payload under an `original_sources` or equivalent custody path, record its hash, extract additively, create a Phase 38 descendant in a clearly separate path, and verify licensing, imports/wiring, execution, tests, and release inclusion as separate gates. Promote only after evidence-backed review.

## Maintenance rule

This index records the public state observed on 2026-08-05. Future custody captures must be additive, dated, and reviewable. Do not rewrite an existing hash to match a changed attachment; add a new observation and explain the relationship.
