# CONTRIBUTING

**Read this before opening an issue or pull request.**

BLOOMCORE is not a casual open-source project.
Contributions are welcome, but only if they respect the system’s purpose,
structure, and invariants.

This document explains what contributions are accepted and how they are evaluated.

---

## Core expectation

BLOOMCORE exists to preserve:
- continuity
- authorship
- coherence
- long-horizon accountability

Contributions that undermine these goals will not be merged,
regardless of technical merit.

---

## Who should contribute

You should consider contributing only if you:

- have read `00_START_HERE.md`
- understand the shared control loop
- respect strict slice boundaries
- are comfortable with strong licensing
- are willing to receive structural feedback

If you are looking for:
- quick wins
- drive-by PRs
- feature farming
- opinion debates

This is not the right repository.

---

## Types of contributions we accept

We welcome contributions that:

- fix correctness bugs
- improve clarity or documentation
- strengthen invariants or safety checks
- improve auditability or reproducibility
- reduce ambiguity or surface hidden assumptions
- add tests that enforce existing behavior

All contributions must be **coherence-preserving**.

---

## Types of contributions we do not accept

We do **not** accept contributions that:

- blur slice boundaries
- introduce domain semantics into core layers
- weaken receipt or audit guarantees
- remove or obscure authorship attribution
- bypass licensing or governance flow
- add convenience at the cost of continuity

Feature requests that violate these constraints will be declined.

---

## Process overview

1. **Open an issue first**  
   Describe the problem you believe exists.
   Do not submit a PR without prior discussion.

2. **Explain the invariant**  
   State which invariant your change preserves or strengthens.

3. **Submit a focused PR**  
   Small, surgical changes are preferred.
   Large refactors require explicit approval.

4. **Expect structural review**  
   Feedback may focus on boundaries and implications,
   not just code style or performance.

---

## Pull request requirements

All pull requests must:

- reference an approved issue
- include tests where applicable
- preserve authorship headers
- pass CI checks
- comply with licensing requirements
- include a signed CLA (see below)

PRs that fail these checks will not be reviewed.

---

## Contributor License Agreement (CLA)

All contributors must sign the **Contributor License Agreement (CLA)**.

This is required so contributions may be included in future
dual-licensed releases.

If you have not signed the CLA:
- your PR will fail CI
- it will not be reviewed

See `CLA.md` for details.

---

## Code style and conventions

- Favor clarity over cleverness
- Prefer explicit over implicit behavior
- Avoid hidden state
- Make invariants machine-checkable where possible
- Document assumptions

BLOOMCORE is optimized for auditability, not terseness.

---

## Communication norms

- Be precise
- Be respectful
- Avoid ideology
- Avoid hype
- Avoid personal attacks

Disagreements should reference:
- invariants
- failure modes
- reproducibility

Not opinions.

---

## Final note

Contributing to BLOOMCORE means contributing to a **system spine**,
not a feature set.

If that excites you, welcome.

If it frustrates you, it’s better to know now.

