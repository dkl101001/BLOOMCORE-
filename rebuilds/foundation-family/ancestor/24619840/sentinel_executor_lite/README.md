# Sentinel Executor LITE (v0.1.0)

Executor LITE is the **actuator half** of Sentinel.

- **Kernel** decides and emits `EXEC_*` command receipts into an append-only ledger.
- **Executor** tails that ledger, verifies evidence-gates, and performs the requested action via a backend.
- **No policy authority lives here.** Executor never escalates; it only executes allowed commands and reports results as receipts.

## What Executor LITE needs (only)
1) **Kernel ledger file path** (JSONL receipts)
2) **Default evidence gate set** (provided by this package; override later if desired)
3) **Backend config** (enabled backends + parameters)

---

## Install

```bash
python -m pip install .
```

## Quick start (NOOP backend)

```bash
executorctl run --ledger ~/.sentinel/ledger.jsonl --backend-config ~/.sentinel/executor.backends.json
```

Example backend config:

```json
{
  "active_backend": "noop",
  "backends": {
    "noop": {},
    "process": {
      "allow_pids": [],
      "allow_cmd_regex": ["^python", "^bash", "^sentinel"],
      "signal_map": { "PAUSE": "STOP", "RESUME": "CONT", "SHUTDOWN": "TERM" }
    },
    "file_patch": {
      "artifacts_dir": "~/.sentinel/artifacts",
      "install_dir": "~/.sentinel/installed_artifacts"
    }
  }
}
```

---

## Receipt contract (minimum)

Kernel emits command receipts:
- `EXEC_PATCH_PLAN`
- `EXEC_PATCH_APPLY`
- `EXEC_PAUSE_SET`
- `EXEC_SANDBOX_ENTER`
- `EXEC_ISOLATE_ENTER`
- `EXEC_SHUTDOWN_REQUEST`

Executor emits result receipts:
- `EXEC_ACK`
- `EXEC_DONE`
- `EXEC_FAIL`

---

## Evidence gates (default)

High-impact actions require hard evidence already present in the ledger.

Hard evidence kinds (default):
- `BINARY_IOC_CONFIRMED`
- `HONEYTOKEN_TRIP`
- `INTEGRITY_BREAK_CONFIRMED`

Commands requiring evidence (default):
- `EXEC_ISOLATE_ENTER`
- `EXEC_SHUTDOWN_REQUEST`

---

## CLI

```bash
executorctl run --ledger PATH --backend-config PATH [--state PATH] [--poll-ms 250] [--dry-run]
executorctl status --ledger PATH
executorctl replay --ledger PATH --from-hash HASH [--limit 50]
executorctl backends --backend-config PATH
executorctl dry-run --ledger PATH --backend-config PATH --limit 50
```

---

## License

Commercial / proprietary. See `LICENSE-COMMERCIAL.txt`.
