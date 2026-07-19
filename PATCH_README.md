# ECA Public Custody Hardening Patch

**Created:** 2026-07-18T23:14:42-04:00 / 2026-07-19T03:14:42+00:00  
**Intended use:** GitHub/publication hardening patch for an already-public ECA release  
**Custody posture:** Public-facing, defensive, non-enabling, BLOOMCORE-bound

## Purpose

This patch is for a public ECA repository or publication that already exists. It does not treat secrecy as the primary defense. Instead, it makes public stewardship harder to invert by binding ECA to BLOOMCORE field law, anti-coercion constraints, provenance, audit, and misuse detection.

The central rule is:

```text
ECA is not valid as an unbound control grammar.
ECA is only valid when bound to BLOOMCORE field law, accountability infrastructure, non-coercion constraints, receipt integrity, public/private custody membranes, and accountable replay.
```

## Recommended application order

1. Add `DISCLAIMER.md` at repository root.
2. Add `BLOOMCORE_BINDING.md` at repository root.
3. Add `ANTI_INVERSION_BOUNDARY.md` at repository root.
4. Add `PUBLIC_PRIVATE_BOUNDARY.md` at repository root.
5. Add `DEFENSIVE_AUDIT_GUIDE.md` at repository root or `/docs/`.
6. Add `PROVENANCE_AND_CUSTODY.md` at repository root.
7. Add `MISUSE_REPORTING.md` and `CONTRIBUTING.md` if public collaboration is accepted.
8. Link these files from the repository README.

## File map

- `DISCLAIMER.md` — non-militarization and anti-coercion boundary.
- `BLOOMCORE_BINDING.md` — states that ECA must remain subordinate to BLOOMCORE field law.
- `ANTI_INVERSION_BOUNDARY.md` — defines healthy roles, inverted roles, and forbidden use classes.
- `PUBLIC_PRIVATE_BOUNDARY.md` — separates public-safe interface material from withheld implementation-sensitive details.
- `DEFENSIVE_AUDIT_GUIDE.md` — gives good actors a way to recognize ECA inversion through observable behavior.
- `PROVENANCE_AND_CUSTODY.md` — preserves authorship, lineage, versioning, and custody requirements.
- `MISUSE_REPORTING.md` — gives a safe path to report suspected inversion or coercive use.
- `CONTRIBUTING.md` — contribution requirements for anti-inversion, custody, and public/private boundary compliance.

## Non-overwrite warning

Do not blindly overwrite an existing README, license, or governance file. Merge this patch intentionally. Preserve existing authorship, dates, commit history, and prior-publication evidence.
