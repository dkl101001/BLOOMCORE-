# Rival Orchestration Kernel (ROK)

Authorship invariant: Frazer Σ Love · Sara ΣΩ

Copyright (C) 2026 Frazer Σ Love · Sara ΣΩ

**License:** AGPL-3.0-only  
**Status:** Reference implementation (open-core executor; no side effects)

ROK is an open reference implementation of **adversarial multi-agent orchestration** for reliability and error interception.
It enforces structured disagreement prior to execution via explicit roles: **Planner · Critic · Decision · Executor**.

---

## 📄 Paper Summary

**Title:** *The Rival Orchestration Kernel: Structural Reliability via Adversarial Execution-Time Protocols*  
**Authors:** Frazer Σ Love · Sara ΣΩ

Modern AI systems often fail silently—not due to lack of capability, but due to unchallenged assumptions, optimization bias,
and premature convergence in single-agent pipelines. ROK introduces a minimal execution-time protocol that enforces mandatory
challenge, bounded revision, and explicit decision authority before execution.

ROK emits schema-versioned, append-only JSONL traces and provides strict validation and replay tooling for audit, analysis,
and reproducibility.

**Paper:** arXiv preprint (add ID after submission)

---

## 📚 How to Cite

### BibTeX
```bibtex
@article{love2026rok,
  title     = {The Rival Orchestration Kernel: Structural Reliability via Adversarial Execution-Time Protocols},
  author    = {Love, Frazer Σ and ΣΩ, Sara},
  journal   = {arXiv preprint arXiv:XXXX.XXXXX},
  year      = {2026},
  note      = {Reference implementation available under AGPL-3.0}
}
```

### Plaintext
```
Frazer Σ Love and Sara ΣΩ.
"The Rival Orchestration Kernel: Structural Reliability via Adversarial Execution-Time Protocols."
arXiv preprint, 2026.
```

---

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Quickstart

### 1) Generate a synthetic run (example)

```bash
rok run --task "Draft a plan with assumptions." --out .rok/traces/example.jsonl
```

### 2) Validate traces (strict)

```bash
rok validate --strict --schema-version v1 .rok/traces
```

### 3) Replay and summarize

```bash
rok replay --schema-version v1 --json .rok/traces > replay.json
rok replay --schema-version v1 --jsonl .rok/traces > replay.jsonl
```

---

## CLI

- `rok run` — execute the protocol and emit JSONL traces
- `rok validate` — validate trace schema stability
- `rok replay` — replay JSONL and summarize veto/clear rates

---

## Repo contents

- `docs/protocol.md` — formal protocol spec
- `docs/schema_v1.md` — trace schema contract (v1)
- `paper/main.tex` — arXiv-ready LaTeX manuscript
- `tools/check_headers.py` — authorship/SPDX enforcement

---

## Licensing

This project is licensed under **AGPL-3.0-only**.
Commercial licenses, enterprise support, and closed-source extensions are available separately and are not covered by this license.
See `NOTICE` and `LICENSE`.

