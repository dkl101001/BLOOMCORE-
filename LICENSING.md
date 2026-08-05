# BLOOMCORE Public Licensing Guide

This is a plain-language orientation to the repository's path-based licenses. The complete license texts control. This guide is not legal advice.

## Which license applies?

Check in this order:

1. the SPDX identifier in the file;
2. an explicit license notice in the nearest directory;
3. the path map in [`LICENSE.md`](LICENSE.md);
4. the repository's default `AGPL-3.0-only` license.

| Material | Default open-source license |
|---|---|
| `docs/faq/**` | Apache-2.0 |
| Expressly marked public schemas, examples, and documentation | Apache-2.0 |
| Expressly marked standalone validators and audit utilities | MPL-2.0 |
| Inherited material, integrated runtimes, services, and unmarked files | AGPL-3.0-only |

## Apache-2.0 materials

Apache-2.0 is a permissive license. Follow its conditions when redistributing the work or derivative works, including preservation of applicable notices and provision of the license.

Use of Apache-2.0 material does not require a BLOOMCORE Commercial License merely because the surrounding project is closed-source.

## MPL-2.0 materials

MPL-2.0 is file-level copyleft. Its obligations generally attach when covered source or executable forms are distributed outside an organization. Read the complete MPL-2.0 text for the requirements that apply to source availability, notices, and modified covered files.

Use of an MPL-2.0 file does not automatically place unrelated files under MPL-2.0.

## AGPL-3.0-only materials

AGPL-3.0-only is the default for unmarked and inherited material. It includes source-availability obligations for covered programs, including the additional Section 13 obligation when users interact remotely through a computer network with a modified covered program.

The exact scope of a derivative or combined work is fact-specific. Read the complete license and obtain legal advice for a proprietary integration.

## Commercial licensing

A separate BLOOMCORE Commercial License may be available for AGPL-covered material where the licensors have authority to grant it. The commercial grant does not apply automatically to third-party material or expand beyond its own scope.

Apache-2.0 and MPL-2.0 materials remain available under their stated open-source licenses.

## Existing material

This multi-license map does not relicense inherited files by implication. Any intentional reclassification requires verified copyright authority, preservation of required notices, and an explicit change.

## Project purpose

[`ETHICAL_USE.md`](ETHICAL_USE.md) states the project's non-coercion and anti-weaponization purpose. Open-source licenses and the ethical statement serve different functions; the latter does not silently modify the former.

## Complete texts

- Root `LICENSE`: AGPL-3.0-only
- `LICENSES/Apache-2.0.txt`
- `LICENSES/MPL-2.0.txt`
- `LICENSES/AGPL-3.0-only.txt` when mirrored from the root license

