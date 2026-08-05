<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Foundation Release Family Rebuild

This is the first additive rebuild of the BLOOMCORE public release lineage. It joins the seven-release foundation family, from `V1.0` through `V1.0.0.5`, without changing a historical tag, release record, or attachment.

## Preservation layout

- `original_sources/` contains the eight release-body ZIP payloads byte-for-byte. These archives are the custody authority for this rebuild.
- `ancestor/<attachment-id>/` contains reviewable expansions of those archives. Generated Python and pytest caches are deliberately excluded; the expanded trees are not substitutes for the ZIPs.
- `phase38-descendant/` is new AGPL-3.0-only work. It supplies an ancestral NumPy oracle and a separately executable Full Fire JAX backend.
- `CUSTODY_MANIFEST.sha256.json` binds release identity, attachment identity, byte length, and SHA-256.
- `LICENSE_DISPOSITION.md` records what may be integrated and what remains custody-only.
- `EVIDENCE.md` states what has actually been executed and what remains outside the verified aperture.

## Family order

| Order | Tag | Exact release title | Preserved payloads | Descendant role |
|---:|---|---|---:|---|
| 1 | `V1.0` | BLOOMFORCE- Core Engine v0.1.0 | 1 | bounded force contract |
| 2 | `v1.0` | LAW.WISECORE.v1 Membrane Engine | 1 | truth/phase/Wu-Wei/friend gate |
| 3 | `V1.0.0.1` | BLOOMCORE Pseudospectral PDE Core Engine | 1 | pseudo-spectral field carrier |
| 4 | `V1.0.0.2` | Sentinel LITE kernel and umbrella | 2 | allow/suppress boundary; executor excluded |
| 5 | `V1.0.0.3` | BLOOMCORE Continuity Spine | 1 | continuity/telemetry boundary |
| 6 | `V1.0.0.4` | BLOOMCORE CPU Toy | 1 | identity, coherence, fracture, memory oracle |
| 7 | `V1.0.0.5` | World Engine v0.1 | 1 | hash-chained receipt surface |

“Phase 38 descendant” means a proposed, additive implementation informed by the supplied Phase 38 canon. It does not retroactively rename the releases or claim that the historical payloads already implemented Phase 38.
