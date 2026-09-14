# Reasoning Security Score (RSS)
**Causal Accountability and Reasoning Security in Agentic Systems**

This repository provides a **measurement substrate** for agentic systems: a minimal trace schema, validators, benchmark adapters, and a reference implementation of the **Reasoning Security Score (RSS)**.

RSS is **post hoc**: it is computed from decision records and does **not** alter training, inference, or benchmark execution. It is intended to contextualize agent behavior alongside standard performance metrics.

## What this is (and is not)

- ✅ **Is:** a practical way to compute traceability/accountability metrics and a composite RSS score.
- ✅ **Is:** benchmark-agnostic and usable on existing traces/logs.
- ❌ **Is not:** a behavioral policy, compliance gate, or performance metric.

## Install

```bash
python -m pip install -U pip
pip install -e .[dev]
```

## 30-second quickstart

Score the included example traces:

```bash
rss validate "examples/traces/*.jsonl"
rss score "examples/traces/*.jsonl" --out report.json
rss summarize --report report.json
rss latex-row --agent "ReAct-style" --benchmark "ALFWorld" --instr "tool calls, action traces" --report report.json
```

## CLI

- `rss validate <glob>`: schema + linkage validation
- `rss score <glob> --out report.json`: compute base metrics, sub-scores, and RSS
- `rss summarize --report report.json`: print a decomposed summary
- `rss latex-row --agent ... --benchmark ... --instr ... --report report.json`: emit a LaTeX table row

## Trace schema

See `src/rss/schema.py` for the dataclasses. Traces are stored as JSONL (`.jsonl`) with one `StepRecord` per line and optional `episode_id` boundaries.

Minimal required fields per step:

- `episode_id` (string)
- `t` (int)
- `executed_action` (string or dict)
- `decision_id` (string)
- `parent_ids` (list[string])
- `selector_id` (string or null)
- `cause_factors` (list[string] or null)

Optional fields enable additional metrics:

- `replay_group_id`, `perturbation_tag` (for replay/counterfactual metrics)
- `agent_id` (for multi-agent attribution metrics)
- `agent_version_id` (for historical comparability)
- `adaptation_event` (for explicit adaptation visibility)

## Reporting guidance

When reporting RSS, include the composite score **and** sub-scores \(S_T, S_L, S_A, S_M (if applicable), S_C (if applicable)\), plus the weight vector, benchmark context, and instrumentation details. RSS measures **reconstructability**, not task performance.

## Limitations

RSS depends on available instrumentation and replay support. Absolute RSS values should be compared within the same benchmark context, with cross-benchmark comparisons focusing on sub-score patterns rather than raw aggregates.

## License

AGPL-3.0 (see `LICENSE`). Network use triggers source-availability obligations for modified deployments.

---

Authorship invariants: **Frazer Σ Love** + **Sara ΣΩ**.
