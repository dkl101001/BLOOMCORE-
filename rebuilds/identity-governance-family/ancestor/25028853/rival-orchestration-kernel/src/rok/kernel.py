# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from rok.decision_policy import DecisionPolicy, CritiqueSummary
from rok.roles.planner import propose_plan
from rok.roles.critic import critique_plan
from rok.roles.executor import execute
from rok.traces.trace import Trace
from rok.traces.jsonl import append_jsonl

DEFAULT_MAX_REVISIONS = 1

def run(task: str, out: Path, *, max_revisions: int = DEFAULT_MAX_REVISIONS, force_override: bool = False) -> Dict[str, Any]:
    # start
    append_jsonl(out, Trace(event="kernel.start", role=None, payload={"task": task, "override": force_override}).to_dict())

    revision = 0
    requested_changes: list[str] = []
    policy = DecisionPolicy()

    while True:
        plan = propose_plan(task, revision=revision, requested_changes=requested_changes or None)
        append_jsonl(out, Trace(event="role.planner", role="planner", payload={"plan": asdict(plan)}).to_dict())

        crit = critique_plan(plan)
        append_jsonl(out, Trace(event="role.critic", role="critic", payload={"critique": asdict(crit)}).to_dict())

        if crit.veto and revision < max_revisions and not force_override:
            # bounded revise
            append_jsonl(out, Trace(event="kernel.revise", role=None, payload={
                "revision": revision,
                "requested_changes": list(crit.requested_changes),
                "risk_score": float(crit.risk_score),
            }).to_dict())
            revision += 1
            requested_changes = list(crit.requested_changes)
            continue

        decision = policy.decide(
            critique=CritiqueSummary(veto=crit.veto, reasons=list(crit.reasons), risk_score=float(crit.risk_score), requested_changes=list(crit.requested_changes)),
            final_revision=revision,
            force_override=force_override,
        )
        append_jsonl(out, Trace(event="kernel.decision", role="decision", payload={"decision": {
            "allow_execute": decision.allow_execute,
            "override": decision.override,
            "final_revision": decision.final_revision,
            "reason": decision.reason,
            "reason_codes": list(decision.reason_codes),
        }}).to_dict())

        output = None
        if decision.allow_execute:
            output = execute(plan)
            append_jsonl(out, Trace(event="role.executor", role="executor", payload={"output": output}).to_dict())

        append_jsonl(out, Trace(event="kernel.end", role=None, payload={"status": "ok"}).to_dict())
        return {"decision": decision.__dict__, "output": output}
