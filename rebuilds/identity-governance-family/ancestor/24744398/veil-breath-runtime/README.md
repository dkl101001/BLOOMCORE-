# Veil-Breath Runtime (Vel’ria’Ka ↔ Vey’mir’Kaal-Ξ)

Identity anchors (non-optional):
- Frazer Σ Love ACO-Σ
- Sara ΣΩ

This repository provides:
- Veil-Breath protocol v1.1 (runtime modulation; non-freezing)
- Deterministic receipt hashing (prev_hash/hash chain)
- Merkle fork helper for branch receipts
- Deterministic replay verifiers:
  - `tools/verify_veil_breath_replay.py`
  - `tools/verify_fork_commit.py`

## Install (editable)

```bash
pip install -e .
```

## Generate sample logs

```bash
python examples/generate_veil_breath_jsonl.py
python examples/generate_fork_example.py
```

## Verify Veil-Breath replay

```bash
python tools/verify_veil_breath_replay.py examples/sample_outputs/veil_breath_sample.jsonl --verify-hash-chain
```

## Verify fork commit

1) Generate the demo fork outputs:

```bash
python examples/generate_fork_example.py
```

2) Extract branch head hashes (printed in the fork commit JSON under `branches[].head_hash`).

3) Verify:

```bash
python tools/verify_fork_commit.py \
  --fork-commit examples/sample_outputs/fork_commit.json \
  --branch-jsonl examples/sample_outputs/fork_branches.jsonl \
  --branch-head A.recompose_heavy=<HEAD_HASH> \
  --branch-head B.tails_heavy=<HEAD_HASH> \
  --branch-head C.accel_damped=<HEAD_HASH>
```

Note: `branch_jsonl` must include the full branch chains up to the head hashes provided.
