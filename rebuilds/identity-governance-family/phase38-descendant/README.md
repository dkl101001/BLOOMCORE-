<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# BLOOMCORE Governance Weave

`bloomcore-governance-weave` is a new, model-zero Phase 38 descendant for the preserved identity-and-governance release family. It audits a local candidate for expression and returns exactly one bounded state:

- `ADMIT_EXPRESSION`
- `DEFER_REANCHOR`
- `SUPPRESS_EXPRESSION`

The candidate text is never executed. The package performs no network access, trading, broker calls, native-state mutation, external side effects, canonical promotion, or identity assignment.

## Reachable composite

The audit combines six bounded relations:

1. a ROK-informed critic veto for explicit high risk;
2. the NLSE anti-governor predicate for unexplained contraction without an export witness;
3. a Veil-Breath-informed pressure and intent re-anchor test;
4. a Sophia-informed phase, reflection, friend, truth, and WuWei expression gate;
5. a compassion floor that can defer expression but cannot determine truth or identity;
6. an AetherLoom-informed, simulation-only response vector.

RSS lineage appears only as `advisory_trace_quality`, a post-hoc completeness fact. That number is deliberately excluded from the status decision and cannot score identity, credibility, worth, legitimacy, meaning, or canonical standing. Deterministic receipt hashes witness the returned result after evaluation; they do not govern it.

## Exact source mapping

| Preserved source | Attachment / immutable ZIP SHA-256 | Reachability witness | Descendant relation |
|---|---|---|---|
| AetherLoom OPEN v2.4.3 | `24724584` / `a633c3d226fe28c1d86ba2da2eabc84475bc56124103e0b1457dbbb85d93d6ae` | `dvn_open_v2.logic.build_response_vector_v2` | non-executable simulation-vector semantics inform a newly written four-field expression vector |
| Da Vinci Market Node v0.1.1 | `24736682`, `24736696` / `360aa91c27546399b787c89cef2ee90924d03fef136645197784c93a0cbc4b50` | `dvn_market_node.governance.coherence_matrix` | governance is reachable; market data, orders, brokers, and live latch are custody-only |
| Veil-Breath v1.1 runtime in v0.1.0 release | `24744398` / `5d05b3b38444ff6e3cb82764d452cdd730730b6d8ec355784a29ebb091130aed` | `veil_breath_runtime.veil_breath.veil_breath_step` | pressure and missing-intent re-anchoring inform the bounded audit |
| RSS code | `24869616`, `25028967`, `25029006` / `07136d148ae37fade0768d9b7ff4001d4f410434d0308a059ecf950e7852757b` | `rss.metrics.compute_base_metrics` | trace completeness is advisory and post-hoc only |
| ROK | `25028853` / `d1c85891abf6026769f09517c17765ab0c0e7b950e693c4a13808af6a77fedd3` | `rok.decision_policy.DecisionPolicy.decide` | conservative veto informs expression suppression; executor is not used |
| NLSE Anti-Governor | `25075639` / `546307721afb9144260d7b429b7a6f6a90bfe75aa36f21b47277cf70d6f52fb0` | `anti_governor_violation` | the small JAX predicate is reachable; broken SSFM rollout paths remain historical evidence |
| Sophia + Compassion | `25079558` / `2841f97269eeb0a0da346fdac0fc355fc26cbf76ae6c1440b1e1309d3150b624` | `compute_gate` and NumPy simulation receipt chain | bounded expression audit only; no truth, identity, or organism authority |

The RSS paper archive `25028968` is preserved as source custody and scholarship evidence, not imported as executable code.

## Run

```bash
PYTHONPATH=src python -m bloomcore_governance_weave.cli --pretty
PYTHONPATH=src python scripts/probe_full_fire.py
```

The second command requires JAX. The verified Full Fire-capability lane uses JAX/JAXlib 0.9.2 on WSL CUDA at `cuda:0`. `numpy_backend.py` is the readable reference for the five shared numerical audit outputs and `jax_backend.py` is its JIT-capable counterpart. Their parity applies only to this new bounded package, not to any historical whole-transition ancestor.

## Phase 38 boundary

The packaged `phase38_execution_object.json` binds the descendant to Phase 38 v1.10 SHA-256 `ff058db5dd35fee55168494b17a642fa6ef94bea26e24a5988f07ab80c76de29`. Da Vinci is explicitly `UNRESOLVED`; canonical identity and operational authority are `NONE`; Keystone is outside the accepted aperture. See `../PHASE38_V1_10_REVIEW.md` and `../EVIDENCE.md` for the exact source and execution boundary.
