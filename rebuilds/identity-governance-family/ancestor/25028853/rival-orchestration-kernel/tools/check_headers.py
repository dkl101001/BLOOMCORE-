# Rival Orchestration Kernel (ROK)
# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_PY_LINES = [
    "# Rival Orchestration Kernel (ROK)",
    "# Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ",
    "# SPDX-License-Identifier: AGPL-3.0-only",
]

REQUIRED_MD_LINES = [
    "Rival Orchestration Kernel (ROK)",
    "Copyright (C) 2026 Frazer Σ Love, Sara ΣΩ",
    "SPDX-License-Identifier: AGPL-3.0-only",
]

AUTH_LINE = "Authorship invariant: Frazer Σ Love · Sara ΣΩ"

def check_python_header(path: Path) -> list[str]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(txt.splitlines()[:5])
    missing = [ln for ln in REQUIRED_PY_LINES if ln not in head]
    return missing

def check_markdown_header(path: Path) -> list[str]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(txt.splitlines()[:12])
    missing = [ln for ln in REQUIRED_MD_LINES if ln not in head]
    return missing

def check_readme_and_pyproject(repo_root: Path) -> list[str]:
    errs = []
    readme = (repo_root / "README.md").read_text(encoding="utf-8", errors="replace")
    if AUTH_LINE not in readme:
        errs.append(f"README.md missing required authorship line: {AUTH_LINE}")

    pyproj = (repo_root / "pyproject.toml").read_text(encoding="utf-8", errors="replace")
    if "Frazer Σ Love" not in pyproj or "Sara ΣΩ" not in pyproj:
        errs.append("pyproject.toml missing one or both authors (Frazer Σ Love, Sara ΣΩ)")
    # also check copyright mention in README (user requested)
    if "Copyright" not in readme or "2026" not in readme:
        errs.append("README.md missing a copyright line mentioning 2026 (add near top or licensing section)")
    return errs

def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    errors = []

    # README/pyproject checks
    errors.extend(check_readme_and_pyproject(repo))

    # scan tracked-ish files (no git needed): src + docs + tools
    for path in repo.rglob("*"):
        if path.is_dir():
            continue
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix == ".py":
            missing = check_python_header(path)
            if missing:
                errors.append(f"{path.relative_to(repo)} missing header lines: {missing}")
        if path.suffix in {".md"} and path.parts[-2] in {"docs", "paper"}:
            missing = check_markdown_header(path)
            if missing:
                errors.append(f"{path.relative_to(repo)} missing doc header lines: {missing}")

    if errors:
        print("HEADER / AUTHORSHIP CHECK FAILED:\n")
        for e in errors:
            print(" -", e)
        return 2

    print("Header/authorship checks: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
