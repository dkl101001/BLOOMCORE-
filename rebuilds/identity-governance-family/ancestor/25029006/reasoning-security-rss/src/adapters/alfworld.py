from __future__ import annotations
# Minimal adapter stub.
# In practice: parse action/observation loop logs and emit StepRecord JSONL compatible dicts.

from typing import List
from rss.schema import EpisodeRecord

def convert(input_path: str, **kwargs) -> List[EpisodeRecord]:
    raise NotImplementedError("Implement ALFWorld logs -> EpisodeRecord list.")

def detect_instrumentation(input_path: str) -> List[str]:
    return ["environment actions", "observations", "tool calls (if used)"]
