# DO I NEED A COMMERCIAL LICENSE?

**Short answer:**  
If you are keeping your source code closed, **yes**.

This document helps you determine which license applies to your use of BLOOMCORE.

It is written to be read quickly and answered honestly.

---

## Start here

Answer the following questions in order.

Do not skip ahead.

---

## 1. Are you using BLOOMCORE at all?

- ❌ No → You do not need a license.
- ✅ Yes → Continue.

---

## 2. Are you distributing BLOOMCORE or a derivative work?

Distribution includes:
- shipping binaries
- publishing containers
- embedding in products
- offering as SaaS or API
- internal deployment accessible to others

- ❌ No → Continue.
- ✅ Yes → Continue.

*(Network access counts as distribution under AGPL.)*

---

## 3. Is your project fully open source?

“Fully open source” means:
- your entire codebase is published
- BLOOMCORE and all modifications are included
- users can access the exact source running in production

- ✅ Yes → You may use BLOOMCORE under **AGPL-3.0** at no cost.
- ❌ No → Continue.

---

## 4. Are you willing to publish your source code?

This includes:
- your modifications to BLOOMCORE
- any tightly coupled integration code
- the version actually deployed

- ✅ Yes → Use **AGPL-3.0**.
- ❌ No → You need a **commercial license**.

---

## 5. Are you using BLOOMCORE internally at a for-profit organization?

- ❌ No → Continue.
- ✅ Yes → Continue.

If the system is:
- closed source
- not disclosed to users or employees

→ You need a **commercial license**.

---

## 6. Are you offering a closed SaaS, API, or proprietary product?

- ❌ No → Continue.
- ✅ Yes → You need a **commercial license**.

---

## 7. Are you mixing BLOOMCORE with proprietary code you cannot release?

- ❌ No → Continue.
- ✅ Yes → You need a **commercial license**.

---

## 8. Are you unsure or uncomfortable with AGPL obligations?

- ❌ No → You likely qualify for **AGPL-3.0**.
- ✅ Yes → You should obtain a **commercial license**.

AGPL is a reciprocal license.
If reciprocity creates risk for you, choose the commercial option.

---

## Common examples

### Open research project
- Source published
- Modifications disclosed

→ **AGPL-3.0 applies.**

---

### Startup building a closed product
- Proprietary code
- No public source

→ **Commercial license required.**

---

### Internal enterprise system
- Closed source
- Used by employees

→ **Commercial license required.**

---

### Personal experiment
- Local use only
- No distribution

→ **AGPL-3.0 applies.**

---

## Attribution still applies

Regardless of license choice, you must preserve:

- copyright notices
- license headers
- authorship attribution:
  - Frazer Σ Love ACO-Σ
  - Sara ΣΩ

These are system invariants.

---

## Still unsure?

If you are still uncertain after reading this file:

- Review `LICENSING.md`
- Review `LICENSING_FLOWCHART.md`
- Contact the maintainers

If you proceed without clarity, you assume the risk.

---

## Final note

This is not meant to be adversarial.

The license exists to:
- protect authorship
- prevent silent enclosure
- keep powerful systems inspectable

If you want to build closed systems, that option exists.
It simply requires a commercial agreement.

