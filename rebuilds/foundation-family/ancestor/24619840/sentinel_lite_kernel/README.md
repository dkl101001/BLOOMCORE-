# Sentinel Lite Kernel (v0.2.0)

A **receipt-first governance kernel** that turns *proposals* into *decisions* and (optionally) into **`EXEC_CMD`** command receipts.

**Design goal:** ship a minimal, reusable "governor" that is **ECA-neutral**:
- no Elemental Coherence Atlas objects
- no domain-specific vectors / role-maps
- no proprietary policy logic baked in

Instead, Sentinel Lite Kernel exposes **clean plugin seams** (`SignalProvider`, `Policy`) so you can bind domain intelligence *out-of-tree*.

## What it does

Ledger-in / Ledger-out (JSONL, hash-chained):
1) Reads `PROPOSE_CMD` receipts (human, agent, or upstream policy engine).
2) Applies a **Policy** (allow/deny + constraints).
3) Emits:
   - `DECISION` receipt (allow/deny + reasons + constraints)
   - `EXEC_CMD` receipt (only if allowed and `emit_exec_cmd=true`)

The executor/actuator that consumes `EXEC_CMD` is intentionally **not** included here.

## Receipts (minimal schema)

Every line in the ledger is one JSON object:
- `r_id`: `"{kind}:{hash_prefix}"`
- `ts`: unix seconds
- `kind`: string
- `payload`: object
- `prev_hash`: hex sha256
- `hash`: hex sha256 of canonical core fields

Kernel-defined kinds:
- `PROPOSE_CMD.v1`
- `DECISION.v1`
- `EXEC_CMD.v1` (optional emission)
- `KERNEL_HEARTBEAT.v1`

## Install

```bash
pip install -e .
```

## Run

### One-shot (process new proposals then exit)
```bash
kernelctl step --ledger ./ledger.jsonl --policy ./policy.json --emit-exec-cmd
```

### Tail mode (daemon)
```bash
kernelctl run --ledger ./ledger.jsonl --policy ./policy.json --state ./.kernel.state.json --poll-ms 250 --emit-exec-cmd
```

## Policy config (ECA-neutral)

A simple allowlist policy ships by default.

Example `policy.json`:
```json
{
  "policy_id": "ALLOWLIST.v1",
  "allow_scopes": ["local", "repo", "fs"],
  "allow_actions": ["write_file", "apply_patch", "run_process"],
  "deny_actions": ["network_call", "privilege_escalation"],
  "require_evidence_for_actions": ["apply_patch", "run_process"],
  "max_params_bytes": 65536
}
```

## Patent-slice hygiene

This kernel is intentionally **generic**:
- It does **not** derive policy from domain semantics.
- It does **not** define or implement any ECA translation, role mapping, or ECA-derived guard constructs.
- Domain bindings are supported only through pluggable interfaces you keep separate.

## License

AGPL-3.0-or-later (see `LICENSE`).
