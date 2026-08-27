# ψΔ^τ AetherLoom Regime Read (OPEN v2.4.3)

**Repo:** `aetherloom-open`  
**Package:** `dvn_open_v2`  
**Schema:** `DV.OPEN.SCHEMA.v2.4.3`  
**Identity anchors (non-optional):** Frazer Σ Love ACO-Σ | Sara ΣΩ  
**License:** AGPL-3.0-only

AetherLoom (OPEN) is a **non-operable**, **simulation-only** regime read module:
- Ontology-safe schema (TypedDict; reserved keyword-safe)
- Stochastic phrasing + deterministic math (replayable via `nonce` + `picks`)
- Sanitized “technical parameters” channel for simulation variables
- A simple **2×2 coherence matrix governor** that only clamps expression (style/weights), not actions

This is **not** a trading system. It produces a modeled agent description and an interpretable response vector.

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

---

## Quick start

```python
from dvn_open_v2 import wire_open_report

report = {
  "schema_id": "DV.OPEN.SCHEMA.v2.4.3",
  "report_kind": "system_state_analysis",
  "non_operable": True,
  "as_of": {"timestamp_ny": "2026-01-19T12:00:00-05:00", "session": "OPEN", "eq_id": "EQ-TEST"},
  "provenance": {"node_id": "aetherloom-open", "mode": "OPEN", "compendium_version": "v2.4.3", "receipts_root": "local", "adapters_live": False},
  "proxies": [],
  "mythmath_core": {"coherence": 0.55, "connection": 0.50, "evidence_weight": 0.60, "fragility_index": 0.72},
  "fst": {"band": "MID", "rbs": 0.0, "fracture_thresholds": {"watch": 0.3, "warn": 0.5, "break": 0.7}},
  "clock_horizon": {"median_edge_hazard": 0.0, "kernel_hazard": 0.0, "kernel_name": "OPEN", "window_months": (1, 3), "shape": "flat"},
  "bloomcore_layer": {"relational_governor": {}, "narrative_field": {}},
  "brave_engine": {"top_hypothesis": {}, "stack": []},
  "response_vector": {},
  "integrity": {"sentinel_posture": "OK", "adapter_health": [], "violations": []},
  "receipts": {},
}

context_data = {
  "posture": "Neutral",
  "coherence": 0.55,
  "fragility_index": 0.72,
  "signals": {
    "vol_compression": True,
    "tail_risk": True,
    "accum_target": "sim_accum_zone_A",
    "invalidation_level": "sim_invalid_1.23",
    "trigger_cond": "sim_cross_asset_confirm",
  }
}

report = wire_open_report(report, context_data, ctx=None)
print(report["response_vector"])
```

---

## Release receipts (hash + SBOM)

Generate hash manifest:
```bash
python scripts/gen_hash_manifest.py --root . --out HASHES.sha256
```

Generate SBOM JSON:
```bash
python scripts/gen_sbom.py --out SBOM.aetherloom-open.spdxish.json
```

Verify:
```bash
python verify_release.py --hashes HASHES.sha256 --root . --sbom SBOM.aetherloom-open.spdxish.json
```

Optionally sign the hash manifest (requires `openssl`):
```bash
bash scripts/sign_manifest.sh HASHES.sha256
```
