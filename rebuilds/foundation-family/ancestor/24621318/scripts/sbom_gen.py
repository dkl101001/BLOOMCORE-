#!/usr/bin/env python3
"""Generate SBOMs for BLOOMFORCE-CORE.

Outputs:
- sbom/sbom.cdx.json   (CycloneDX 1.5 JSON, minimal)
- sbom/sbom.spdx.json  (SPDX 2.3 JSON, minimal)

Notes:
- This project intentionally has no runtime deps.
- If you add dependencies later, extend this generator accordingly.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read_pyproject_version() -> str:
    p = os.path.join(ROOT, "pyproject.toml")
    with open(p, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("version ="):
                return ln.split("=", 1)[1].strip().strip('"')
    return "0.0.0"


def _git(cmd: list[str]) -> str:
    try:
        out = subprocess.check_output(["git", *cmd], cwd=ROOT, stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return ""


def main() -> int:
    name = "bloomforce-core"
    version = _read_pyproject_version()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    commit = _git(["rev-parse", "HEAD"])
    repo = _git(["config", "--get", "remote.origin.url"])

    os.makedirs(os.path.join(ROOT, "sbom"), exist_ok=True)

    # CycloneDX 1.5 (minimal)
    cdx = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:00000000-0000-0000-0000-000000000000",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "tools": [{"vendor": "bloomforce-core", "name": "sbom_gen.py", "version": "1"}],
            "component": {
                "type": "library",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{name}@{version}",
            },
        },
        "components": [],
        "dependencies": [{"ref": f"pkg:pypi/{name}@{version}", "dependsOn": []}],
        "properties": [
            {"name": "vcs.commit", "value": commit or ""},
            {"name": "vcs.remote", "value": repo or ""},
        ],
    }

    # SPDX 2.3 JSON (minimal)
    spdx = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"{name}-{version}",
        "documentNamespace": f"https://example.invalid/spdx/{name}/{version}",
        "creationInfo": {
            "created": now,
            "creators": [
                "Tool: bloomforce-core/sbom_gen.py",
            ],
        },
        "packages": [
            {
                "name": name,
                "SPDXID": "SPDXRef-Package-bloomforce-core",
                "versionInfo": version,
                "downloadLocation": "NOASSERTION",
                "licenseConcluded": "MIT",
                "licenseDeclared": "MIT",
                "supplier": "NOASSERTION",
                "filesAnalyzed": False,
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": f"pkg:pypi/{name}@{version}",
                    }
                ],
                "annotations": [
                    {
                        "annotationDate": now,
                        "annotationType": "OTHER",
                        "annotator": "Tool: bloomforce-core/sbom_gen.py",
                        "comment": f"vcs.commit={commit or ''} vcs.remote={repo or ''}",
                    }
                ],
            }
        ],
        "relationships": [],
    }

    with open(os.path.join(ROOT, "sbom", "sbom.cdx.json"), "w", encoding="utf-8") as f:
        json.dump(cdx, f, indent=2, sort_keys=True)

    with open(os.path.join(ROOT, "sbom", "sbom.spdx.json"), "w", encoding="utf-8") as f:
        json.dump(spdx, f, indent=2, sort_keys=True)

    print("Wrote: sbom/sbom.cdx.json")
    print("Wrote: sbom/sbom.spdx.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
