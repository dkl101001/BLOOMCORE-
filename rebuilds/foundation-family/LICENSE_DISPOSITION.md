<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# License and Integration Disposition

This is a provenance and implementation record, not legal advice. Historical files retain their own notices and licenses. Extraction does not relicense them, and the new descendant does not absorb a component merely because its payload is preserved nearby.

| Payload | Declared or observed status | Rebuild disposition |
|---|---|---|
| BLOOMFORCE | root package declares MIT; two release scripts carry `AGPL-3.0-only` identifiers | preserved and contract-tested; mixed per-file notices retained; no wholesale copy into descendant |
| WISECORE | `AGPL-3.0-only` | preserved; inherited GPU import defect documented; repaired gate written anew in AGPL descendant |
| Pseudospectral PDE Engine | `AGPL-3.0-only` | preserved; inherited JAX state/pytree defect documented; field transition rebuilt in AGPL descendant |
| Sentinel LITE kernel | `AGPL-3.0-or-later` | preserved and contract-tested; allow/suppress semantics represented in descendant |
| Sentinel Executor LITE | commercial placeholder / all rights reserved | custody-only; never imported, executed, or copied into descendant |
| Continuity Spine | `AGPL-3.0-only` | preserved and reachability-tested; descendant emits compatible bounded telemetry facts rather than copying the package |
| CPU Toy | `AGPL-3.0-only` | preserved and tested; selected numerical operators inform the descendant mapping without establishing whole-transition ancestry parity |
| World Engine | no license declaration found in the payload root or `pyproject.toml` | preserved and reachability-tested only; license status unclear; no source copied into descendant |
| Phase 38 descendant | `AGPL-3.0-only` under the repository default | new additive code |

The commercial Sentinel executor and the license-unclear World Engine cannot be treated as generally reusable open-source implementation material based on this payload set. The descendant’s receipt chain is an independently written deterministic witness and does not claim World Engine licensing or authority.
