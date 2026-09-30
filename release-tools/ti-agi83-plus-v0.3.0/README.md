<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# TI-AGI83+ v0.3.0 release custody

Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.

This folder preserves the exact locally verified source archive, detached checksum, verification record and full README release body. App source is pinned to commit `fa36e44229149705d60f2d0a55c144d2a4c94b5d`.

The dedicated workflow verifies the unchanged archive and its equality to repository app bytes, installs into an isolated environment, and runs backend/HTTP and actual browser tests from clean extraction. Only its dependent publication job can create the new release. The job uses GitHub's short-lived repository token; no personal credentials or stored secrets are needed. Verification has read-only repository permissions; the publication job requests the contents permission needed to publish this release. No paid runner, recurring schedule, external service or unrelated repository change is configured.

The tag identifies the exact app source commit. The release carries the README, source ZIP, checksum, original measured verification and independent CI verification. It does not replace the repository's global latest release. Re-running publication against an existing tag/release fails rather than overwriting earlier custody.

Workflow availability and successful publication must be observed separately; these files are not proof that a release exists.
