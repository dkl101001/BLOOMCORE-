<!--
Rival Orchestration Kernel (ROK)
Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
SPDX-License-Identifier: AGPL-3.0-only
-->

# Rival Orchestration Protocol

This document defines the **formal execution protocol** implemented by the Rival Orchestration Kernel (ROK).

ROK is an execution-time reliability mechanism. It enforces adversarial review *before* execution through explicit role
separation and bounded revision.

## Roles

- **Planner**: proposes a structured plan (steps, assumptions, constraints).
- **Critic**: evaluates the plan adversarially; can veto with reason codes.
- **Decision**: applies explicit policy gates; resolves veto/override; authorizes execution.
- **Executor**: executes only if authorized; reference executor is side-effect free.

## Protocol

1. `kernel.start`
2. `role.planner` emits `plan`
3. `role.critic` emits `critique` (may veto)
4. If veto and revision budget remains: bounded loop
   - `kernel.revise`
   - `role.planner` revised plan
   - `role.critic` re-critique
5. `kernel.decision` emits allow/deny, override, final revision, reason codes
6. If allowed: `role.executor`
7. `kernel.end`

## Guarantees

- No silent execution after veto
- Bounded revision (no infinite loops)
- Schema-versioned, append-only traces suitable for strict validation and replay
