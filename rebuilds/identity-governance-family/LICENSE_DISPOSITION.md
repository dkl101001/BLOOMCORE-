<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# License and Integration Disposition

This is a provenance and implementation record, not legal advice. Historical files retain their original notices. Extraction does not relicense an archive, and a nearby payload is not automatically reusable source.

| Payload | Declared or observed status | Rebuild disposition |
|---|---|---|
| AetherLoom OPEN | package metadata declares `AGPL-3.0-only`; bundled license is an incomplete replacement notice rather than the full license | preserved and safely reachability-tested; selected non-executable semantics inform newly written code |
| Da Vinci Market Node | package metadata declares `AGPL-3.0-only` | both identical attachment records preserved; governance surface tested; market-data, order, broker, Alpaca, and live-execution paths remain custody-only |
| Veil-Breath Runtime | declares AGPL v3 | preserved; pressure/re-anchor and receipt-chain surfaces tested; new code is independently written |
| RSS code archives | declare AGPL v3 | three attachment records preserved as exact duplicate bytes; one representative code tree tested; metrics remain advisory only |
| RSS paper bundle | paper sources and compiled artifacts preserved; per-file notices retained | scholarship custody only; not imported into descendant runtime |
| ROK | package metadata declares `AGPL-3.0-only`; bundled license is a short pointer rather than full terms | policy surface tested; executor not integrated; new adversarial audit independently written |
| NLSE Anti-Governor | package metadata declares `AGPL-3.0-only`; bundled `LICENSE` is an error placeholder | preserved; small anti-closure predicate safely exercised; no historical source copied; broken rollout paths disclosed |
| Sophia + Compassion | root license contains only the identifier `AGPL-3.0-or-later` | preserved and reachability-tested; formulas inform a newly written bounded expression audit |
| Governance Weave descendant | complete `AGPL-3.0-only` text shipped in `phase38-descendant/LICENSE.md` | new additive code |

The incomplete historical license files are preserved as residue and must not be presented as complete license delivery. The descendant therefore ships its own complete AGPL-3.0-only text and does not wholesale copy any historical package. This repository’s broader multi-license policy remains distinct from the license actually attached to this bounded descendant.
