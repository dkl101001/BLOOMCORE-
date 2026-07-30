# BLOOMCORE Public Licensing Map

BLOOMCORE Public uses multiple licenses by file and path. This file explains which license applies; it does not replace the license texts or any explicit SPDX identifier in an individual file.

## Default license

Unless a file, directory, or section below states otherwise, material in this repository remains licensed under **GNU Affero General Public License v3.0 only (`AGPL-3.0-only`)**, consistent with the repository's existing root `LICENSE`.

## Path-specific licenses

| Material | License | Scope |
|---|---|---|
| `docs/faq/**` | `Apache-2.0` | Public FAQ, glossary, relationship map, source matrix, open-question register, and README insertion text |
| Newly added public schemas and examples carrying an `Apache-2.0` SPDX identifier | `Apache-2.0` | Adoption-facing specifications, examples, and documentation only |
| Newly added standalone validators or audit utilities carrying an `MPL-2.0` SPDX identifier | `MPL-2.0` | Only the expressly marked file or directory |
| All other repository material unless expressly marked | `AGPL-3.0-only` | Existing code, integrated runtimes, services, and inherited material |

An unmarked file does not become Apache-2.0 or MPL-2.0 merely because it is conceptually related to documentation, validation, or examples.

## Commercial licensing

Where the existing `NOTICE`, `LICENSING.md`, `DO_I_NEED_A_COMMERCIAL_LICENSE.md`, or `LICENSE-COMMERCIAL.txt` offers a separate BLOOMCORE Commercial License, that commercial license remains a separate grant. It does not erase the open-source license applicable to an open-source copy, and this path map does not expand or narrow the commercial grant.

## SPDX identifiers

New files should carry one of these identifiers when practical:

```text
SPDX-License-Identifier: Apache-2.0
SPDX-License-Identifier: MPL-2.0
SPDX-License-Identifier: AGPL-3.0-only
```

For Markdown, an HTML comment may be used:

```html
<!-- SPDX-License-Identifier: Apache-2.0 -->
```

## License texts

- Root `LICENSE`: existing `AGPL-3.0-only` text
- `LICENSES/Apache-2.0.txt`
- `LICENSES/MPL-2.0.txt`
- `LICENSES/AGPL-3.0-only.txt`: optional duplicate of the root AGPL text for SPDX-style tooling

## Relicensing boundary

Existing files are not reclassified by implication. Moving inherited material into a differently licensed directory, changing a filename, or quoting it in new documentation does not by itself change its license. Any intentional relicense requires verified copyright authority, preservation of notices, and an explicit repository change.

This licensing map is repository documentation, not legal advice.

