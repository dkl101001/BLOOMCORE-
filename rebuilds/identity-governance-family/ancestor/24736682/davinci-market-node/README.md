# ψΔ^τ Da Vinci Market Node (OPEN) — v0.1.0

**Identity anchors (non-optional):** Frazer Σ Love ACO-Σ | Sara ΣΩ  
**License:** AGPL-3.0-only

A Bloomberg-class terminal replacement is **six systems wearing one coat**:
Data → Research → Decision → Risk → Execution → Audit.

This repo ships the **execution-capable spine** (OSS prior art standard):
- **Streaming-ready adapter interfaces** (ships with a synthetic feed)
- **Parameterized strategy plugin** (`ORB_VWAP.v0`) that emits typed `OrderIntent`s
- **Risk engine** (pre-trade checks + clamps)
- **Broker adapter** (`alpaca` + `paper`)
- **Receipt-first ledger** (JSONL) + compendium markdown output
- **Sentinel Lite / Mirrorseed Lite / Dreamloop Lite** (structural standards)

It is designed to be **non-deterministic but replayable** via `eq_id + nonce`.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Run (OPEN pulse)

Synthetic feed + Alpaca broker selected by default; paper trading base URL is default.

```bash
dvn-open --asof 2025-11-10T09:30:00-0500 --broker paper
```

Replay stochastic phrasing/perturbations:

```bash
dvn-open --asof 2025-11-10T09:30:00-0500 --broker paper --nonce deadbeef
```

### Alpaca execution

Set env:
- `APCA_API_KEY_ID`
- `APCA_API_SECRET_KEY`
- `APCA_API_BASE_URL` (defaults to paper)

**Live latch:** if base URL is live, you must set `DVN_LIVE_ENABLE=1`.

```bash
export APCA_API_KEY_ID=...
export APCA_API_SECRET_KEY=...
export APCA_API_BASE_URL=https://paper-api.alpaca.markets

dvn-open --asof 2025-11-10T09:30:00-0500 --broker alpaca
```

## Outputs

- `./compendium_out/YYYY-MM-DD/open.md`
- `./compendium_out/state.json` (auto patch bump)
- `./receipts.jsonl` (append-only)

## Strategy is parameterized

The shipped strategy is a **module**: it emits intents when its **parameters** and **market-frame features** pass.
You can tune in `EngineConfig` or by forking the strategy.

## Prior-art boundary

This repo ships **interfaces, auditability, and execution plumbing**.
Keep proprietary slices private by implementing them as private strategy modules or private governance transforms.
