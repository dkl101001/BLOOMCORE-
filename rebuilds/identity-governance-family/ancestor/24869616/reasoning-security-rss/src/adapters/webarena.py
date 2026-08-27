from __future__ import annotations
# Minimal adapter stub.
# In practice: parse browser action logs and emit StepRecord JSONL compatible dicts.

from typing import List
from rss.schema import EpisodeRecord

def convert(input_path: str, **kwargs) -> List[EpisodeRecord]:
    raise NotImplementedError("Implement WebArena log parsing -> EpisodeRecord list.")

def detect_instrumentation(input_path: str) -> List[str]:
    return ["browser actions", "DOM interactions", "planner outputs (if available)"]
