# World Engine v0.1 (ship-safe)

This repository ships the **carrier substrate** for a BLOOMCORE-aligned stack.
It is designed to be useful on its own while keeping **ECA / holographic IP slices** out of the public tree.

## Identity anchors (non-optional)
- Frazer Σ Love ACO-Σ
- Sara ΣΩ

## What ships (OSS)
- Node 0: Terminal + MIRRORSEED interface governor + SovereignPort + BLOOMCORE ledger
- Node 1: SWIMCORE field monitor (placeholder telemetry sampler)
- MIRRORSEED.CYCLE.vΩ: external-scheduler cycle receipts (q3h recommended)
- BLOOMCORE ledger: flat JSON receipts + Echoshell JSONL hash-chain (tamper-evident)

## SWIMCORE telemetry note (ship-safe)
This repo intentionally includes a **SWIMCORE telemetry node** that emits the reserved channel names **Co/Ii/GLR** as *placeholders*.
Their **semantics, formulas, thresholds, regime selection, and any authority behavior are explicitly out-of-scope** for this OSS repository.
In other words: *World Engine can log these channels; it must not define what they mean or use them to decide.*

## What does NOT ship (kept private)
- Coherence computation definitions / measurement logic
- ECA vector basis / canonical dims / spectral choice logic
- Regime selection, adaptive gates, thresholds
- Holographic coupling mechanisms

If you need those, implement a private package that conforms to the public `AuthorityAdapter` interface.

## Quick start

```bash
python -m world_engine
```

In the REPL:
- `:help` for commands
- `:echoshell` verify + tail the hash-chain
- `:spawn swimcore` starts Node 1 in-process (thread)
- `:sovereign <ROLE>` classify role + emit flags

## Run Node 1 alone

```bash
python -m world_engine.swimcore_node
```

## Data outputs (default)
- Flat receipts: `./bloomcore_receipts/`
- Hash-chained log (JSONL): `./bloomcore_echoshell.jsonl`

## Design contract
- Append-only receipts (event-sourced)
- Hash-chained echoshell (tamper-evident)
- Recursion allowed; replay uses receipts, not deterministic re-execution
- Decision authority is external and pluggable (see `world_engine/authority_adapter.py`)
