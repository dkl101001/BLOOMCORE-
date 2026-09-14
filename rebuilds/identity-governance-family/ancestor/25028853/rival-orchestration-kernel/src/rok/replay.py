# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from rok.taxonomy import REASON_CODES


@dataclass
class RunStat:
    file: str
    run_id: Optional[str] = None
    start_ts: Optional[str] = None
    end_ts: Optional[str] = None

    schema_version: Optional[str] = None
    schema_versions_seen: List[str] = field(default_factory=list)

    outcome: str = "UNKNOWN"  # CLEARED | VETOED | OVERRIDE_FORCED | UNKNOWN
    allow_execute: Optional[bool] = None
    override: Optional[bool] = None
    final_revision: Optional[int] = None

    revision_count: int = 0   # count of kernel.revise events
    decision_codes: List[str] = field(default_factory=list)
    critique_reasons: List[str] = field(default_factory=list)


@dataclass
class ReplaySummary:
    files: int = 0
    runs: int = 0

    vetoed: int = 0
    cleared: int = 0
    override_forced: int = 0

    override_rate: float = 0.0
    avg_revision_count: float = 0.0

    decision_code_counts: Dict[str, int] = field(default_factory=dict)
    critique_reason_counts: Dict[str, int] = field(default_factory=dict)

    schema_versions_present: List[str] = field(default_factory=list)

    series: List[Dict[str, Any]] = field(default_factory=list)
    per_run: List[RunStat] = field(default_factory=list)

    def bump(self, d: Dict[str, int], key: str, n: int = 1) -> None:
        d[key] = int(d.get(key, 0)) + n


def iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _classify_outcome(allow: Optional[bool], override: Optional[bool]) -> str:
    if allow is True and override is True:
        return "OVERRIDE_FORCED"
    if allow is True:
        return "CLEARED"
    if allow is False:
        return "VETOED"
    return "UNKNOWN"


def _enforce_schema_pin(*, path: Path, versions_seen: set, schema_version: Optional[str]) -> None:
    if schema_version is None:
        return
    if not versions_seen:
        raise ValueError(f"schema_version pin failed for {path}: no schema_version found in file.")
    if any(v != schema_version for v in versions_seen):
        raise ValueError(
            f"schema_version pin failed for {path}: expected '{schema_version}' but saw {sorted(list(versions_seen))}"
        )


def replay_paths(paths: List[Path], *, schema_version: Optional[str] = None) -> ReplaySummary:
    s = ReplaySummary(files=len(paths))

    for p in paths:
        s.runs += 1
        run = RunStat(file=str(p))

        versions_seen: set = set()
        last_decision: Optional[dict] = None
        last_critique: Optional[dict] = None

        for evt in iter_jsonl(p):
            event = evt.get("event")
            payload = evt.get("payload", {})
            ts = evt.get("ts")

            sv = evt.get("schema_version")
            if isinstance(sv, str) and sv:
                versions_seen.add(sv)
                if run.schema_version is None:
                    run.schema_version = sv

            if event == "kernel.start":
                run.start_ts = ts
                if isinstance(payload, dict):
                    run.run_id = payload.get("run_id")

            if event == "kernel.end":
                run.end_ts = ts

            if event == "kernel.revise":
                run.revision_count += 1

            if event == "kernel.decision":
                last_decision = payload.get("decision", {}) if isinstance(payload, dict) else {}
                codes = last_decision.get("reason_codes", []) or []
                run.decision_codes = [str(c) for c in codes]
                for code in run.decision_codes:
                    s.bump(s.decision_code_counts, code)

            if event == "role.critic":
                last_critique = payload.get("critique", {}) if isinstance(payload, dict) else {}
                reasons = last_critique.get("reasons", []) or []
                run.critique_reasons = [str(c) for c in reasons]
                for code in run.critique_reasons:
                    s.bump(s.critique_reason_counts, code)

        run.schema_versions_seen = sorted(list(versions_seen))
        _enforce_schema_pin(path=p, versions_seen=versions_seen, schema_version=schema_version)

        if isinstance(last_decision, dict) and last_decision:
            run.allow_execute = bool(last_decision.get("allow_execute", False))
            run.override = bool(last_decision.get("override", False))
            run.final_revision = last_decision.get("final_revision")
        else:
            run.allow_execute = None
            run.override = None
            run.final_revision = None

        run.outcome = _classify_outcome(run.allow_execute, run.override)

        if run.outcome == "OVERRIDE_FORCED":
            s.override_forced += 1
        elif run.outcome == "CLEARED":
            s.cleared += 1
        elif run.outcome == "VETOED":
            s.vetoed += 1

        s.per_run.append(run)

        s.series.append(
            {
                "file": run.file,
                "run_id": run.run_id,
                "start_ts": run.start_ts,
                "end_ts": run.end_ts,
                "schema_version": run.schema_version,
                "schema_versions_seen": list(run.schema_versions_seen),
                "outcome": run.outcome,
                "override": run.override,
                "revision_count": run.revision_count,
                "final_revision": run.final_revision,
            }
        )

    total = max(1, s.runs)
    s.override_rate = float(s.override_forced) / float(total)
    s.avg_revision_count = float(sum(r.revision_count for r in s.per_run)) / float(total)

    present = set()
    for r in s.per_run:
        for v in (r.schema_versions_seen or []):
            present.add(v)
    s.schema_versions_present = sorted(list(present))

    if schema_version is not None and s.schema_versions_present != [schema_version]:
        raise ValueError(
            f"schema_version pin failed: expected only '{schema_version}' but present={s.schema_versions_present}"
        )

    return s


def format_summary(s: ReplaySummary, *, top_k: int = 10) -> str:
    lines: List[str] = []
    lines.append(f"files={s.files} runs={s.runs}")
    lines.append(f"cleared={s.cleared} vetoed={s.vetoed} override_forced={s.override_forced}")
    lines.append(f"override_rate={s.override_rate:.3f} avg_revision_count={s.avg_revision_count:.3f}")
    if s.schema_versions_present:
        lines.append(f"schema_versions_present={s.schema_versions_present}")

    def top_items(d: Dict[str, int]) -> List[Tuple[str, int]]:
        return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:top_k]

    lines.append("")
    lines.append("Top decision reason codes:")
    for code, n in top_items(s.decision_code_counts):
        meta = REASON_CODES.get(code)
        title = meta.title if meta else ""
        lines.append(f"  {code}  {n}" + (f"  ({title})" if title else ""))

    lines.append("")
    lines.append("Top critique reason codes:")
    for code, n in top_items(s.critique_reason_counts):
        meta = REASON_CODES.get(code)
        title = meta.title if meta else ""
        lines.append(f"  {code}  {n}" + (f"  ({title})" if title else ""))

    lines.append("")
    lines.append("Per-run (last 10):")
    for r in s.per_run[-10:]:
        lines.append(
            f"  {Path(r.file).name}: outcome={r.outcome} revs={r.revision_count} override={r.override} "
            f"final_rev={r.final_revision} schema={r.schema_version}"
        )

    return "\n".join(lines)


def summary_to_json_dict(s: ReplaySummary) -> Dict[str, Any]:
    return {
        "files": s.files,
        "runs": s.runs,
        "cleared": s.cleared,
        "vetoed": s.vetoed,
        "override_forced": s.override_forced,
        "override_rate": s.override_rate,
        "avg_revision_count": s.avg_revision_count,
        "schema_versions_present": list(s.schema_versions_present),
        "decision_code_counts": dict(s.decision_code_counts),
        "critique_reason_counts": dict(s.critique_reason_counts),
        "series": list(s.series),
        "per_run": [asdict(r) for r in s.per_run],
    }


def stream_run_summaries(paths: List[Path], *, schema_version: Optional[str] = None) -> Iterator[Dict[str, Any]]:
    for p in paths:
        run = RunStat(file=str(p))
        versions_seen: set = set()

        last_decision: Optional[dict] = None
        last_critique: Optional[dict] = None

        for evt in iter_jsonl(p):
            event = evt.get("event")
            payload = evt.get("payload", {})
            ts = evt.get("ts")

            sv = evt.get("schema_version")
            if isinstance(sv, str) and sv:
                versions_seen.add(sv)
                if run.schema_version is None:
                    run.schema_version = sv

            if event == "kernel.start":
                run.start_ts = ts
                if isinstance(payload, dict):
                    run.run_id = payload.get("run_id")

            if event == "kernel.end":
                run.end_ts = ts

            if event == "kernel.revise":
                run.revision_count += 1

            if event == "kernel.decision":
                last_decision = payload.get("decision", {}) if isinstance(payload, dict) else {}
                codes = last_decision.get("reason_codes", []) or []
                run.decision_codes = [str(c) for c in codes]

            if event == "role.critic":
                last_critique = payload.get("critique", {}) if isinstance(payload, dict) else {}
                reasons = last_critique.get("reasons", []) or []
                run.critique_reasons = [str(c) for c in reasons]

        run.schema_versions_seen = sorted(list(versions_seen))
        _enforce_schema_pin(path=p, versions_seen=versions_seen, schema_version=schema_version)

        if isinstance(last_decision, dict) and last_decision:
            run.allow_execute = bool(last_decision.get("allow_execute", False))
            run.override = bool(last_decision.get("override", False))
            run.final_revision = last_decision.get("final_revision")
        else:
            run.allow_execute = None
            run.override = None
            run.final_revision = None

        run.outcome = _classify_outcome(run.allow_execute, run.override)

        yield {
            "file": run.file,
            "run_id": run.run_id,
            "start_ts": run.start_ts,
            "end_ts": run.end_ts,
            "schema_version": run.schema_version,
            "schema_versions_seen": list(run.schema_versions_seen),
            "outcome": run.outcome,
            "override": run.override,
            "revision_count": run.revision_count,
            "final_revision": run.final_revision,
            "decision_codes": list(run.decision_codes),
            "critique_reasons": list(run.critique_reasons),
        }


def resolve_inputs(inputs: List[str]) -> List[Path]:
    out: List[Path] = []
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            out.extend(sorted(p.glob("*.jsonl")))
        elif p.is_file():
            out.append(p)
    seen = set()
    uniq = []
    for p in out:
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(p)
    return uniq
