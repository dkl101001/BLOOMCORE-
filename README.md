BLOOMCORE

A system spine for building, auditing, and evolving non-deterministic architectures under pressure.

BLOOMCORE is not a framework, library, or demo.
It is a continuity-preserving system spine.

It exists for work that must:
	•	run for years, not weeks
	•	survive drift, failure, and hostile conditions
	•	remain accountable without freezing evolution
	•	preserve authorship, lineage, and intent over time

⸻

Why BLOOMCORE exists

Modern systems increasingly rely on:
	•	non-deterministic computation
	•	adaptive components
	•	recursive processes
	•	distributed execution

Most stacks optimize for speed and flexibility, then try to bolt on:
	•	governance
	•	audits
	•	safety
	•	attribution

Those additions fail once systems begin to change themselves.

BLOOMCORE starts from the opposite assumption:

Non-determinism is inevitable.
Continuity must therefore be enforced.

⸻

What BLOOMCORE is

BLOOMCORE is a governance and execution substrate for systems that must:
	•	evolve without losing coherence
	•	survive partial failure and human error
	•	maintain decision traceability across versions
	•	remain open without being silently extracted or enclosed

At its core, BLOOMCORE provides:
	•	Receipts, not logs
Decisions are recorded as intentional, reconstructable artifacts.
	•	Coherence checks, not rules engines
Behavior is evaluated structurally, not micromanaged.
	•	Explicit authorship and licensing continuity
Lineage is preserved mechanically, not socially.
	•	Recursion with memory
Systems are allowed to change without erasing their past.

⸻

What BLOOMCORE is not

To avoid confusion:
	•	Not a general-purpose SDK
	•	Not a plug-and-play library
	•	Not a SaaS product
	•	Not “AI governance” theater
	•	Not optimized for short-term velocity

If you are looking for:
	•	a quick dependency
	•	a drop-in compliance tool
	•	a hype-driven framework

This repository is not for you.

⸻

Repository structure (read order)

This repository is intentionally structured.
If you are new, do not start with the code.

00_START_HERE.md          ← orientation + execution order
README.md                 ← this file
LICENSING.md              ← dual-license model
LICENSE                   ← AGPL-3.0 (full text)
LICENSE-COMMERCIAL.txt    ← commercial alternative
DO_I_NEED_A_COMMERCIAL_LICENSE.md
LICENSING_FLOWCHART.md
PRICING.md
CONTRIBUTING.md
CLA.md
.github/
core/                     ← BLOOMCORE-controlled code
contrib/                  ← optional extensions

Start with 00_START_HERE.md.
Everything else assumes you did.

⸻

Licensing (important)

BLOOMCORE is dual-licensed.

Open source (AGPL-3.0)

You may use BLOOMCORE for free if you:
	•	publish the complete corresponding source code
	•	including any deployed or network-accessible versions

Commercial license

You need a commercial license only if:
	•	you use BLOOMCORE in a closed-source system
	•	you deploy it internally at a for-profit organization without disclosure
	•	you run it as a closed SaaS, API, or proprietary product

Rule of thumb

If you keep the source open, it’s free.
If you keep the source closed, you need a commercial license.

See:
	•	LICENSING.md
	•	DO_I_NEED_A_COMMERCIAL_LICENSE.md
	•	LICENSING_FLOWCHART.md

⸻

Contributions

Contributions are welcome only if you understand what you are contributing to.

Key points:
	•	All contributions require agreement to the CLA
	•	Contributions may appear in future dual-licensed releases
	•	This is not a drive-by PR repository

PRs without CLA acknowledgement will fail CI.

See CONTRIBUTING.md and CLA.md.

⸻

Design principles (non-negotiable)

BLOOMCORE operates under enforced invariants:
	•	Truth before comfort
	•	Coherence over velocity
	•	Recursion with memory
	•	No silent mutation
	•	No enclosure without consent

These are not slogans.
They are enforced structurally through receipts, licensing, and governance flow.

⸻

Status

This repository represents an active system spine.
	•	APIs may evolve
	•	Structures may mutate
	•	Receipts preserve continuity across versions

If something feels unfinished, that is intentional.
BLOOMCORE is built to withstand growth, not hide it.

⸻

Authorship & stewardship

BLOOMCORE is authored and stewarded by:
	•	Frazer Σ Love ACO-Σ
	•	Sara ΣΩ

All forks, derivatives, and redistributions must preserve:
	•	license notices
	•	copyright headers
	•	authorship attribution

⸻

Final note

BLOOMCORE is not here to win popularity contests.

It exists to make long-horizon work survivable.

If that resonates, welcome.
If it doesn’t, that’s fine too.

⸻

The shared control loop

This repository is one component of a larger control loop designed for non-deterministic systems:
	•	Computation produces candidate results
	•	WISECORE decides whether results may be emitted
	•	Sentinel Lite decides whether actions are permitted to execute
	•	Continuity Spine records invariant-checked history
	•	Engines and executors apply force to the world

Each layer is intentionally narrow.
No layer replaces another.
No layer is optional once failure cost matters.

The loop allows systems to vary in behavior while remaining auditable, reconstructable, and accountable over time.
