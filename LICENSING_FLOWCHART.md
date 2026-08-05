# Licensing flowchart

Use this path-first guide for a specific file. It summarizes the repository's license map and is not legal advice.

```text
START WITH THE EXACT FILE OR DIRECTORY
  |
  v
Does the file carry an SPDX license identifier?
  |-- YES --> Follow that license.
  |-- NO
        |
        v
Does the nearest containing directory declare a license?
  |-- YES --> Follow that license.
  |-- NO
        |
        v
Is the path listed in LICENSE.md?
  |-- YES --> Follow the mapped license.
  |-- NO  --> Repository default: AGPL-3.0-only.
```

## What each path means

- **Apache-2.0:** permissive reuse of expressly marked adoption-facing documentation, schemas, and examples, subject to its notice and patent terms.
- **MPL-2.0:** file-level copyleft for expressly marked standalone validators or utilities.
- **AGPL-3.0-only:** repository default for inherited and integrated material not expressly classified elsewhere.
- **Commercial:** a separate written grant where offered; it applies only within its stated scope.

## AGPL network boundary

Network use is not simply identical to distribution. AGPL section 13 adds a source-offer obligation when users interact remotely through a network with a **modified covered program**. Whether a particular combined work, deployment, or modification is covered depends on the facts and the license text.

Do not infer that every proprietary codebase touching an AGPL component must automatically be published. Do not infer the opposite either. Review the exact integration and obtain legal advice when the boundary matters.

## Artwork and marks

Documentation licensing does not automatically relicense adjacent binary artwork. The BLOOMCORE name, sigil, logos, and trademarks receive no separate trademark license from this flowchart.

## Still unsure?

Read `LICENSE.md`, the exact license text under `LICENSES/`, and any file header. For commercial rights or a fact-specific interpretation, contact the project steward or qualified counsel before deployment.
