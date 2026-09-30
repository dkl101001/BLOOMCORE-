<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# TI-AGI83+ · next expansions

Version 0.3.0 ships the local table lab and Games. The capabilities below are a development plan, not shipped features. Keep the calculator face, irreverent voice, local custody and inspectable geometric memory as modules grow.

## First: CRM bot

A useful CRM starts with durable records, then assistance over those records.

| Surface | Planned behavior | Completion evidence |
|---|---|---|
| Contacts and companies | Stable IDs, structured details, search, CSV import/export, explicit duplicate review | Import/export round trip; no automatic identity merges |
| Deals | Owner, stage, amount, currency, expected close date; pipeline and totals by currency | Exact decimal calculations; currencies never silently combined |
| Notes and activity | Dated notes linked to records; inspectable source and revision history | Notes survive restart; updates preserve prior versions |
| Follow-ups | Due date, timezone, status and linked contact/deal; a local overdue view | Date-boundary checks; completion and undo are recorded |
| CRM assistance | Draft summaries, next-step suggestions and outreach from selected records | Every factual detail links to current evidence; missing facts remain missing |
| Geometric memory | Typed validation/error patterns in a separate CRM scope | Inspectable projection; learned/flat controls; no spreadsheet or game contamination |

Start with local CRUD, filtering and reversible updates. An optional language model comes later for drafting; the present release has no model integration. Outreach drafts remain drafts until the user authorizes sending through a connected service. A due-date view does not imply background notifications or calendar sync.

## Then: Office-style work

| Module | Planned deliverables | Verification before shipping |
|---|---|---|
| Documents | Letter/report templates, editable drafts, DOCX and PDF export, version history | Open and render output; inspect pagination and preserve supplied text |
| Spreadsheets | XLSX import/export, formatting, common formulas and recalculation, audit/repair integration | Formula grammar and resource limits; totals and round-trip comparisons |
| Presentations | Slide outline, layouts, charts, PPTX and PDF output | Open/render every slide; verify shapes, text and chart values |
| Files and tasks | Local attachment references, reusable templates, linked tasks and search | Stable paths/IDs; missing-file handling; restart and export checks |
| Connected workflows | Optional Microsoft 365 or other document/calendar integrations | Explicit account connection, conflict handling and authorized writes |

These are Office-style workflows and interoperable file formats. Full Microsoft Office compatibility, macros, collaborative editing and unattended account actions require separate design and verification. Preserve originals on import; surface unsupported features before an export can discard them.

## Shared structure

Each module owns typed records, migrations and validators. Shared facilities provide local persistence, stable IDs, transactional changes, evidence history, export and optional geometric retrieval. Current authoritative records decide the work; historical suggestions cannot substitute a contact identity, date, amount or missing source fact.

Do not add inert navigation buttons for planned modules. Add a module when its end-to-end workflow works. Publish each finished expansion twice: code in BLOOMCORE and a tagged release page containing its README, standalone package and measured verification.

Games are a separate recreational surface. Their saved scores are ordinary play records, never an error projection or a CRM signal. Native BLOOMCORE/R20 system admission remains outside this standalone application's scope.
