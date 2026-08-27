# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def family_root() -> Path:
    return Path(__file__).resolve().parents[2]
