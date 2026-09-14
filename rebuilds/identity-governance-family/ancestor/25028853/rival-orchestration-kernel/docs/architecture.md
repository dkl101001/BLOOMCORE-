<!--
Rival Orchestration Kernel (ROK)
Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
SPDX-License-Identifier: AGPL-3.0-only
-->

# Architecture

ROK is a reference kernel that enforces execution-time adversarial review.

Core modules:
- `rok.kernel`: protocol driver (bounded revise–recheck)
- `rok.roles.*`: role implementations (planner/critic/executor)
- `rok.decision_policy`: policy gates & multi-criteria thresholds
- `rok.traces`: schema-versioned JSONL trace emission
- `rok.validate`: schema validation (strict/non-strict)
- `rok.replay`: replay + analytics (batch/streaming)
