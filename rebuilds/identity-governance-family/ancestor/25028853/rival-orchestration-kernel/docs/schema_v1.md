<!--
Rival Orchestration Kernel (ROK)
Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
SPDX-License-Identifier: AGPL-3.0-only
-->

# ROK Trace Schema — v1

Each trace event is one JSON object per line (JSONL). Events are append-only and order-preserving.

## Top-Level Schema

Every line must contain:

```json
{
  "schema_version": "v1",
  "ts": "2026-01-30T18:42:11.381+00:00",
  "event": "kernel.start",
  "role": null,
  "payload": {}
}
```

Fields:
- `schema_version` (string, required): must be `v1`
- `ts` (string, required): ISO-8601 UTC timestamp
- `event` (string, required): event name
- `role` (string|null): emitting role
- `payload` (object): event-specific payload

## Required Events

Non-strict: must include at least `kernel.start` and `kernel.decision`.

Strict mode additionally requires:
- `kernel.end`
- no unknown events
- all lines include matching `schema_version`

## Event Contracts (minimal)

- `kernel.start`: payload may include `task`, `override`
- `role.planner`: payload contains `plan` with `steps`, `assumptions`, `constraints`, `revision`
- `role.critic`: payload contains `critique` with `veto` (bool), `reasons` (list[str]), `risk_score` (float), `requested_changes` (list[str])
- `kernel.revise`: payload contains `revision`, `requested_changes`, `risk_score`
- `kernel.decision`: payload contains `decision` with `allow_execute` (bool), `override` (bool), `final_revision` (int), `reason_codes` (list[str])
- `role.executor`: payload contains `output` (json-safe)
- `kernel.end`: payload contains `status`

Breaking changes require a new schema version.
