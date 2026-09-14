from __future__ import annotations
# Minimal adapter stub.
# In practice: parse patch/diff/test loop and emit StepRecord JSONL compatible dicts.

from typing import List
from rss.schema import EpisodeRecord

def convert(input_path: str, **kwargs) -> List[EpisodeRecord]:
    raise NotImplementedError("Implement SWE-bench traces (diff/test) -> EpisodeRecord list.")

def detect_instrumentation(input_path: str) -> List[str]:
    return ["code diffs", "test outputs", "patch iteration history"]
