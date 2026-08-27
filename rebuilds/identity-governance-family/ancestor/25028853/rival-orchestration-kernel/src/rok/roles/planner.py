# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations
from .base import Plan

def propose_plan(task: str, revision: int, requested_changes: list[str] | None = None) -> Plan:
    # Minimal deterministic planner for reference purposes.
    # Replace with model-backed planner in downstream integrations.
    rc = requested_changes or []
    assumptions = [
        "Inputs are truthful and within scope.",
        "Execution environment is stable.",
    ]
    constraints = [
        "No side effects in reference executor.",
        "Emit trace events for each phase.",
    ]
    steps = [
        "State assumptions and constraints explicitly.",
        "Produce a plan with verification hooks.",
        "Submit plan for adversarial critique.",
    ]
    if rc:
        steps.append(f"Apply requested changes: {', '.join(rc)}")
        constraints.append("All requested changes must be reflected in the revised plan.")
    return Plan(task=task, steps=steps, assumptions=assumptions, constraints=constraints, revision=revision)
