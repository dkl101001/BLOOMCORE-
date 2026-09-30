# SPDX-License-Identifier: AGPL-3.0-only
"""Package only declared source surfaces, with deterministic ZIP metadata."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ti-agi83-plus-v0.3.0"
ROOT_FILES = {"README.md", "LICENSE", "pyproject.toml", ".gitignore"}
SURFACES = {"tiagi83", "tests", "docs", "lineage", "tools"}
SUFFIXES = {".py", ".js", ".html", ".md", ".json", ".toml", ".cjs", ".png"}


def package(output):
    files = {}
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if path.is_symlink() or not path.is_file() or "__pycache__" in rel.parts:
            continue
        if str(rel) in ROOT_FILES or (rel.parts[0] in SURFACES and path.suffix in SUFFIXES):
            if str(rel) != "MANIFEST.sha256.json":
                files[rel.as_posix()] = path.read_bytes()
    manifest = {"schema": "TIAGI.SOURCE-MANIFEST.v1", "algorithm": "sha256",
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}
    files["MANIFEST.sha256.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(PREFIX + "/" + name, date_time=(2026, 9, 30, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    sha = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix + ".sha256").write_text(sha + "  " + output.name + "\n")
    print(json.dumps({"archive": str(output), "sha256": sha, "files": len(files)}))


if __name__ == "__main__":
    package(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / (PREFIX + ".zip"))
