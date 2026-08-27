# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass(frozen=True)
class Plan:
    task: str
    steps: List[str]
    assumptions: List[str]
    constraints: List[str]
    revision: int

@dataclass(frozen=True)
class Critique:
    veto: bool
    reasons: List[str]
    risks: List[str]
    objections: List[str]
    requested_changes: List[str]
    risk_score: float
    notes: str | None = None
