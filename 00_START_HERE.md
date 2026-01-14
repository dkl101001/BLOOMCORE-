# 00_START_HERE

**Read this before you read anything else.**

This repository is not organized like a typical software project.  
If you treat it like one, you will misunderstand it.

This file exists to orient you **before** you touch code, concepts, or opinions.

---

## What BLOOMCORE is (in one paragraph)

BLOOMCORE is a **system spine** for building, governing, and evolving non-deterministic systems over long time horizons.

It is designed for situations where:
- systems change themselves
- behavior cannot be fully predicted
- failure cost is real
- history must remain provable
- authorship and intent must not dissolve over time

If none of that applies to your work, you do not need BLOOMCORE.

---

## What BLOOMCORE is *not*

Before going further, clear these assumptions:

- This is **not** a framework you “adopt”
- This is **not** a library you import casually
- This is **not** a SaaS product
- This is **not** a demo repo
- This is **not** optimized for speed or convenience

BLOOMCORE prioritizes **survivability**, not velocity.

---

## How to read this repository

**Do not start with the code.**  
This is not negotiable.

The repository is structured so that **understanding precedes execution**.

### Recommended read order

1. **`README.md`**  
   High-level purpose, boundaries, and stance.

2. **This file (`00_START_HERE.md`)**  
   Orientation and mental model.

3. **The shared control loop (in `README.md`)**  
   Understand the separation of responsibilities.

4. **Individual component READMEs (in any order)**  
   - Continuity Spine  
   - Sentinel Lite  
   - LAW.WISECORE  
   - BLOOMCORE Engine (Carrier Substrate)  
   - BLOOMFORCE  
   - CPU Prior-Art Toy  

5. **Only then** look at code.

If you skip steps 1–4, the code will look either trivial or confusing.  
Both reactions indicate you started too early.

---

## The mental model you need

BLOOMCORE is **not a single system**.

It is a **control loop composed of narrow, non-overlapping layers**.

Each layer answers exactly one question:

- **Computation / Dynamics**  
  *What state exists and how does it evolve?*

- **BLOOMFORCE**  
  *What pressure is applied?*

- **WISECORE**  
  *May the result be emitted?*

- **Sentinel Lite**  
  *May the action execute?*

- **Continuity Spine**  
  *What actually happened, and can we prove it later?*

No layer replaces another.  
No layer is optional once failure cost matters.

If this separation feels strict, that is intentional.

---

## Why the system is split across repositories

Each repository is:
- independently usable
- independently publishable
- independently auditable

This is not modularity for convenience.  
It is modularity for **accountability**.

If one layer fails, the others must remain legible.

---

## What to do next (choose honestly)

### If you are evaluating
- Read all READMEs
- Ignore implementation details
- Focus on slice boundaries and failure modes

### If you are building
- Identify which single layer you actually need
- Start there
- Do not try to “adopt the whole system”

### If you are extending
- Read `CONTRIBUTING.md` and `CLA.md`
- Expect structural review, not feature feedback
- This is not a drive-by PR repository

### If you are just curious
- That’s fine
- Read, don’t rush
- BLOOMCORE is designed to reward patience

---

## A warning (meant respectfully)

If you are looking for:
- alignment theater
- vague safety language
- hand-wavy governance
- shortcuts around accountability

You will not find them here.

BLOOMCORE is opinionated because the problems it addresses are unforgiving.

---

## Final note

Most systems are built to **move fast**.  
BLOOMCORE is built to **last**.

If that difference matters to you, you’re in the right place.

If it doesn’t, you can walk away now with no loss.

Either way — start by understanding before you execute.
