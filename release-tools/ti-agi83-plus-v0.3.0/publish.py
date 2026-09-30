# SPDX-License-Identifier: AGPL-3.0-only
"""Publish the Operator-authorized release only after the CI verification job."""
import json
import os
from pathlib import Path
import subprocess
from verify_package import verify, TAG, HERE

REPO = "dkl101001/BLOOMCORE-"
SOURCE = "fa36e44229149705d60f2d0a55c144d2a4c94b5d"


def main():
    verify()
    if os.environ.get("GITHUB_REPOSITORY") != REPO or os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise ValueError("Publishing is restricted to this repository's main branch")
    run = os.environ["GITHUB_RUN_ID"]
    workflow_url = "https://github.com/" + REPO + "/actions/runs/" + run
    record = json.loads((HERE / (TAG + "-verification.json")).read_text())
    record["githubActionsVerification"] = {
        "status": "PASS", "workflow": workflow_url,
        "automationCommit": os.environ["GITHUB_SHA"],
        "controls": "Exact ZIP/manifest and source-byte equality, isolated install, backend/HTTP tests, actual browser workflow; publication job requires successful verification job."
    }
    record_path = HERE / (TAG + "-ci-verification.json")
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    body = (HERE / (TAG + "-release-notes.md")).read_text()
    body += "\nGitHub Actions independently verified the exact archive before publication: " + workflow_url + ".\n"
    notes = HERE / "published-readme.md"
    notes.write_text(body)
    assets = [HERE / (TAG + ".zip"), HERE / (TAG + ".zip.sha256"),
              HERE / (TAG + "-verification.json"), record_path, notes]
    subprocess.run(["gh", "release", "create", TAG, *map(str, assets), "--repo", REPO,
                    "--target", SOURCE, "--title", "TEXTERMENTALITY™ · TI-AGI83+ v0.3.0",
                    "--notes-file", str(notes), "--latest=false"], check=True)
    subprocess.run(["gh", "release", "view", TAG, "--repo", REPO, "--json", "url,tagName,isDraft,assets"], check=True)


if __name__ == "__main__":
    main()
