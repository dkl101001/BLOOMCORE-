from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple


def bump_patch(semver: str) -> str:
    parts = semver.strip().lstrip("v").split(".")
    while len(parts) < 3:
        parts.append("0")
    major, minor, patch = parts[:3]
    try:
        patch_i = int(patch)
    except Exception:
        patch_i = 0
    return f"v{major}.{minor}.{patch_i + 1}"


@dataclass
class Compendium:
    root: Path

    def state_path(self) -> Path:
        return self.root / "state.json"

    def read_state(self) -> Dict[str, Any]:
        p = self.state_path()
        if not p.exists():
            return {"compendium_version": "v0.1.0"}
        return json.loads(p.read_text(encoding="utf-8"))

    def write_state(self, state: Dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path().write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def write_markdown(self, date_yyyy_mm_dd: str, filename: str, content: str) -> Path:
        outdir = self.root / date_yyyy_mm_dd
        outdir.mkdir(parents=True, exist_ok=True)
        p = outdir / filename
        p.write_text(content, encoding="utf-8")
        return p
