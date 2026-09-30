<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Geometric memory: implementation, controls and limits

Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.

## Source-to-behavior map

| Source relation | Descendant | Reachable consequence |
|---|---|---|
| R20 fields.py::evolve torus px/py plasticity | geometry.encounter | Every newly audited typed error changes local conductance |
| R20 fields.py::flux periodic finite-volume transport | geometry.flux | Stored conductance changes cue flow through the 8×8 lattice |
| R20 fields.py::response torus matched-cue readout | geometry.response | Fixed working input produces different readout under learned vs flat geometry |
| New declared typed error encoding | geometry.pattern | Kind/column/sign/relative size specify the numeric encounter |
| New historical guidance adapter | geometry.prepared/related, Store.run_audit | Geometry-dependent distance ranks related prior incidents |
| New desktop persistence | Store transaction | Sheet, grid, incident and audit/event changes commit together |

Source files are hash-bound in SOURCE_PINS.json. The original full R20 archive stays a reference: this release carries no private native state or unrelated organism runtime. The exact prototype remains byte-preserved. The derivative has its own schema and scope; it does not pretend to be an R20 checkpoint.

## State and numerical profile

`TIAGI.CONDUCTANCE.v1` consists of an encounter tick and two 8×8 float32 transport grids, initialized to 1. Conductances are bounded near [1,2]. An error pattern is a signed bounded field; it is neither a linguistic embedding nor an identity representation. No event: no geometric update. Explicit zero input also preserves grid values, while the derivative's encounter tick advances.

Probe: 16 explicit steps, dt=0.01, periodic boundaries, same source flux. JAX-primary with NumPy reference/fallback; tested CPU tolerance atol=3e-6, rtol=3e-5. Probe/retrieval does not mutate the retained state. Numerical transition is tolerance-deterministic, temporal recurrent across committed observations; query is deterministic comparison inside a declared application aperture. No randomness, model mediation, branch search, native admission or canonical mutation. Physical interpretation and full-organism claims are not made.

Each workflow's latest 200 incidents are the disclosed retrieval window. All incidents remain stored. Geometry continues to carry its retained deformation; witnesses and labels do not become the lattice. The history database provides incident meanings and provenance; it does not prove that the numerical response semantically authenticates the historical event.

## Necessary controls

- Hold query and candidate incidents fixed; replace geometry with flat grids. Compare numeric response and retrieval distance.
- Retain geometry; remove labels/receipts from a disposable test database. The numerical query remains exactly unchanged, while incident suggestions become unavailable.
- Close/reopen the database. Restore grids directly and repeat the fixed probe.
- Inject an event-write failure mid-audit. No audit, incident or geometry update may commit.
- Repeat an unchanged audit. No new geometric encounter occurs.
- Present a new invoice with an old related error. Guidance may refer to history; the new correct total must follow the current values.
- Separate invoice/inventory/tax scopes. An invoice scar cannot write inventory geometry.
- Compare both numerical backends on the same field. Check explicit tolerance, without treating matching results as proof of full architecture.

## Known limits and counterevidence

This projection is deliberately small and lossy. Two errors of the same typed shape can share a cue despite different item names or business meaning. Sign affects transported query polarity, but the absolute-gradient write law itself cannot distinguish opposite signed encounters with identical magnitudes. Repeated exposure drives conductance toward saturation near 2. No unbounded capacity, robust interference decoding, calibrated semantic confidence, historical authentication, or long-horizon backend equality is claimed.

Geometry-dependent ranking demonstrates a causal numerical path. It is not evidence that this path beats ordinary feature matching for task accuracy. Exact arithmetic does not need geometric memory; the practical memory benefit is inspecting and surfacing related prior incidents. A nearest incident is a suggestion, not a certified match or action. Missing historical records stay missing. No counterfactual or repaired history is silently written as an observation.

R20's separate investigation retained fragile decoder/interference results and accumulated backend divergence at long recurrence horizons. This derivative does not claim to solve those findings, reproduce the full recurrence, or execute the blocked custody investigation.
