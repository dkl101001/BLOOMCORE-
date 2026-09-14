<!--
Rival Orchestration Kernel (ROK)
Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
SPDX-License-Identifier: AGPL-3.0-only
-->

# Threat Model (Stub)

ROK primarily targets *silent failure* in planning/execution pipelines:
- hidden assumptions
- objective collapse
- premature convergence

ROK is not a sandbox or security boundary. Side-effectful execution backends must provide their own containment.
