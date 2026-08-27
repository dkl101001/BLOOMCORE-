# SPDX-License-Identifier: LicenseRef-Sentinel-Commercial
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Any, Dict

from .base import BackendResult

def _expand(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))

@dataclass
class FilePatchBackend:
    name: str = "file_patch"
    artifacts_dir: str = "~/.sentinel/artifacts"
    install_dir: str = "~/.sentinel/installed_artifacts"

    def execute(self, cmd_kind: str, payload: Dict[str, Any]) -> BackendResult:
        artifacts_dir = _expand(self.artifacts_dir)
        install_dir = _expand(self.install_dir)
        os.makedirs(install_dir, exist_ok=True)

        artifact_path = payload.get("artifact_path")
        if artifact_path:
            src = _expand(str(artifact_path))
        else:
            fn = payload.get("filename")
            if not fn:
                return BackendResult(ok=False, detail={"reason": "missing_filename"})
            src = os.path.join(artifacts_dir, str(fn))

        if not os.path.exists(src):
            return BackendResult(ok=False, detail={"reason": "artifact_missing", "src": src})

        dst = os.path.join(install_dir, os.path.basename(src))
        try:
            shutil.copy2(src, dst)
            return BackendResult(ok=True, detail={"installed": dst})
        except Exception as e:
            return BackendResult(ok=False, detail={"reason": "copy_failed", "err": str(e), "src": src, "dst": dst})
