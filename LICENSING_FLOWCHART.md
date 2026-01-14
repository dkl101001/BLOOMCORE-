# LICENSING FLOWCHART

**This file provides a fast, visual way to determine which BLOOMCORE license applies.**

If you want detailed explanations, read:
- `LICENSING.md`
- `DO_I_NEED_A_COMMERCIAL_LICENSE.md`

---

## Quick decision flow (read top to bottom)

```
START
  |
  v
Are you using BLOOMCORE?
  |
  +-- NO --> No license required.
  |
  +-- YES
        |
        v
Is BLOOMCORE distributed or accessed over a network?
(includes SaaS, APIs, internal tools)
        |
        +-- NO --> AGPL-3.0 applies (local/private use).
        |
        +-- YES
              |
              v
Is your entire codebase open source?
(including deployed version)
              |
              +-- YES --> AGPL-3.0 applies.
              |
              +-- NO
                    |
                    v
Are you willing to publish your full source?
                    |
                    +-- YES --> AGPL-3.0 applies.
                    |
                    +-- NO --> COMMERCIAL LICENSE REQUIRED.
```

---

## Interpretation notes

- **Network use counts as distribution** under AGPL-3.0.
- “Open source” means users can access the *exact source* running in production.
- Internal, employee-facing systems count as network use.
- Mixing BLOOMCORE with proprietary code usually triggers commercial licensing.

If you reach “commercial license required,” you must obtain and comply with
`LICENSE-COMMERCIAL.txt`.

---

## Common paths

### Open research / open startup
```
YES → YES → YES
```
→ **AGPL-3.0**

---

### Closed SaaS or API
```
YES → YES → NO → NO
```
→ **Commercial License**

---

### Internal enterprise deployment
```
YES → YES → NO → NO
```
→ **Commercial License**

---

### Local experiment only
```
YES → NO
```
→ **AGPL-3.0**

---

## Attribution still applies

Regardless of which license you use, you must preserve:

- copyright notices
- license headers
- authorship attribution:
  - Frazer Σ Love ACO-Σ
  - Sara ΣΩ

These are system invariants.

---

## Still unsure?

When in doubt:
- choose AGPL-3.0 and publish your source, **or**
- obtain a commercial license

Proceeding without clarity means you assume the risk.

---

## Final reminder

This flowchart is a guide, not a loophole.

BLOOMCORE’s license exists to:
- prevent silent enclosure
- preserve inspectability
- protect authorship

Choose accordingly.
