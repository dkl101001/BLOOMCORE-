# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import subprocess
import sys


def test_family_custody_manifest(family_root):
    result = subprocess.run(
        [sys.executable, str(family_root / "scripts" / "verify_custody.py")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"verified": true' in result.stdout
