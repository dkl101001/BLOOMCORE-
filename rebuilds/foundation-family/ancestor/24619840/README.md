# Sentinel Lite Umbrella

This repo ships **both halves** of Sentinel Lite:

- **sentinel-lite-kernel**: receipt-first *governor* (ECA-neutral)
- **sentinel-executor-lite**: receipt-tail *actuator* (no policy authority)

The two components communicate only through an **append-only JSONL ledger** of hash-chained receipts.

## Layout

- `sentinel_lite_kernel/` — standalone Python package (kernelctl)
- `sentinel_executor_lite/` — standalone Python package (executorctl)
- `LICENSES/` — license texts for each component
- `scripts/` — release hashing + optional SBOM helpers

## Install (dev / editable)

```bash
# from repo root
python -m venv .venv
source .venv/bin/activate
pip install -U pip

pip install -e ./sentinel_lite_kernel
pip install -e ./sentinel_executor_lite
```

## Minimal end-to-end run

Create a policy file:

```bash
cat > policy.json <<'JSON'
{
  "allowed_kinds": ["PROPOSE_CMD.v1"],
  "allow_exec": true,
  "allowed_exec_backends": ["noop", "process", "file_patch"],
  "max_params_bytes": 16384,
  "require_evidence": false
}
JSON
```

Create a ledger and propose a command receipt (example):

```bash
cat >> ledger.jsonl <<'JSON'
{"kind":"PROPOSE_CMD.v1","ts":0,"payload":{"cmd":{"kind":"EXEC_PROCESS.v1","backend":"process","params":{"argv":["echo","hello from executor-lite"]}}},"prev_hash":"","hash":""}
JSON
```

Run the kernel (reads PROPOSE_CMD receipts, emits DECISION + EXEC_* receipts):

```bash
kernelctl step --ledger ./ledger.jsonl --policy ./policy.json --emit-exec-cmd
```

Run the executor (tails ledger, executes EXEC_* receipts, emits RESULT receipts):

```bash
executorctl run --ledger ./ledger.jsonl --config ./sentinel_executor_lite/executor.example.json
```

> Note: the executor ships multiple backends; **do not** enable any backend you do not trust.

## Release hashing / signing

```bash
# from repo root
bash scripts/hash_tree.sh .
bash scripts/sign_release.sh sentinel-lite-umbrella.zip
```

## Licensing

- Kernel is licensed under **AGPL-3.0-or-later** (see `sentinel_lite_kernel/` + `LICENSES/AGPL-3.0-full.txt`)
- Executor Lite uses the **commercial license text** included in `sentinel_executor_lite/` as provided.
  If you want the executor relicensed to AGPL to match the engines, do that as a deliberate, explicit step.
