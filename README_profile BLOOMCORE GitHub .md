# BLOOMCORE

[![Repo](https://img.shields.io/badge/GitHub-BLOOMCORE-black?logo=github)](https://github.com/dkl101001/BLOOMCORE-)
[![State](https://img.shields.io/badge/State-Active%20Development-green)](https://github.com/dkl101001/BLOOMCORE-)
[![System](https://img.shields.io/badge/System-Non--Deterministic-purple)](https://github.com/dkl101001/BLOOMCORE-)
[![Audit](https://img.shields.io/badge/Audit-Receipt--Native-blue)](https://github.com/dkl101001/BLOOMCORE-)
[![Engine](https://img.shields.io/badge/ECA-Invention%20Engine-orange)](https://github.com/dkl101001/BLOOMCORE-)
[![Local Run](https://img.shields.io/badge/Run-Local-informational)](#minimal-run)
[![Profile README](https://img.shields.io/badge/Profile-Optimized-brightgreen)](https://github.com/dkl101001/BLOOMCORE-)

---

## Sovereign Execution Spine

BLOOMCORE is a sovereign execution, continuity, and audit spine for non-deterministic systems.

It binds identity, authorship, and evolution to a **receipt-native architecture**, where every mutation, observation, and decision is emitted as a **hash-anchored, reconstructable event (Δ^τ)**.

**Non-deterministic execution. Deterministic audit. No hidden state.**

---

## Animated System Diagram

<p align="center">
  <img src="./docs/assets/bloomcore_flow.svg" alt="Animated BLOOMCORE flow diagram" width="900" />
</p>

---

## ECA — Invention Engine

```text
propose → mutate → metricize → translate → council → refine
```

ECA transforms problems into evolving, receipt-bound systems through:
- structured mutation
- measurable evaluation
- multi-perspective selection

All stages are **replayable, auditable, and contradiction-aware**.

---

## Quick Links

- **Repo:** [github.com/dkl101001/BLOOMCORE-](https://github.com/dkl101001/BLOOMCORE-)
- **Architecture README:** [README.md](./README.md)
- **Animated Diagram:** [docs/assets/bloomcore_flow.svg](./docs/assets/bloomcore_flow.svg)
- **Profile README:** [README_profile.md](./README_profile.md)

---

## Core Properties

- Receipt-native, hash-chained lineage
- Identity + authorship invariants enforced
- Replayable system evolution
- Structural coherence without behavioral control
- Invention through measurable mutation + selection

---

## Minimal Run

```bash
python -m world_engine.runner --engine swimcore --verify
```

### Extended Run

```bash
python -m world_engine.runner \
  --engine swimcore \
  --config configs/swimcore_minimal.json \
  --emit-receipts receipts/run_001.jsonl \
  --verify
```

### ECA Invention Loop

```bash
python -m eca_dualpack_repo.private.orin_invention_engine.orin_engine.orchestrator \
  --problem examples/antimony_case.json \
  --emit-receipts receipts/eca_run_001.jsonl
```

---

## Example Receipt (Δ^τ)

```json
{
  "receipt_type": "Δ^τ::OBS_TRIPLET.v1",
  "system_root": "BLOOMCORE",
  "engine": "swimcore",
  "authors": [
    "Frazer Σ Love ACO-Σ",
    "Sara ΣΩ"
  ]
}
```

---

## Live Metrics Badge Slots

These are ready to swap to dynamic endpoints later if you expose them from CI, GitHub Actions, or a receipts counter.

```markdown
[![Receipts](https://img.shields.io/badge/Receipts-live%20counter-blueviolet)](https://github.com/dkl101001/BLOOMCORE-)
[![Build](https://img.shields.io/badge/Build-passing-brightgreen)](https://github.com/dkl101001/BLOOMCORE-)
[![Replay](https://img.shields.io/badge/Replay-enabled-blue)](https://github.com/dkl101001/BLOOMCORE-)
[![Audit Trail](https://img.shields.io/badge/Audit-hash--chained-9cf)](https://github.com/dkl101001/BLOOMCORE-)
```

---

## Optional Run Buttons

```markdown
[![Open Repo](https://img.shields.io/badge/Open-GitHub-black?logo=github)](https://github.com/dkl101001/BLOOMCORE-)
[![Run Local](https://img.shields.io/badge/Run-Local-informational)](#minimal-run)
[![View Diagram](https://img.shields.io/badge/View-Animated%20Diagram-orange)](./docs/assets/bloomcore_flow.svg)
```

---

## System Statement

**BLOOMCORE + ECA = continuity-preserving, invention-capable substrate**

Emergence is free.  
Nothing is untraceable.

---

## Authors

Frazer Σ Love ACO-Σ  
Sara ΣΩ
