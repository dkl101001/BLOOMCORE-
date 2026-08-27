#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from importlib.metadata import metadata, requires

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="davinci-market-node")
    ap.add_argument("--out", default="SBOM.davinci-market-node.spdxish.json")
    args = ap.parse_args()

    md = metadata(args.project)
    deps = requires(args.project) or []

    doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"SBOM for {args.project}",
        "documentNamespace": f"urn:uuid:{args.project}-{datetime.now(timezone.utc).isoformat()}",
        "creationInfo": {
            "created": datetime.now(timezone.utc).isoformat(),
            "creators": [
                "Person: Frazer Σ Love ACO-Σ",
                "Person: Sara ΣΩ",
                "Tool: scripts/gen_sbom.py",
            ],
        },
        "packages": [
            {
                "name": md.get("Name", args.project),
                "SPDXID": "SPDXRef-Package-DVN",
                "versionInfo": md.get("Version", "unknown"),
                "downloadLocation": "NOASSERTION",
                "licenseDeclared": md.get("License", "AGPL-3.0-only") or "AGPL-3.0-only",
                "supplier": "NOASSERTION",
                "summary": md.get("Summary", ""),
                "homepage": md.get("Home-page", ""),
            }
        ],
        "dependencies": sorted([d.strip() for d in deps if d.strip()]),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote SBOM -> {args.out} (deps={len(doc['dependencies'])})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
