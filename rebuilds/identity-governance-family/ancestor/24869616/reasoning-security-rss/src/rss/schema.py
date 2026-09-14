from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union, Iterable, Tuple
import json
from pathlib import Path

Action = Union[str, Dict[str, Any]]

@dataclass(frozen=True)
class AdaptationEvent:
    event_id: str
    kind: str
    scope: str
    delta_fingerprint: str
    granularity_score: Optional[float] = None

@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    parent_ids: List[str] = field(default_factory=list)
    selector_id: Optional[str] = None
    selector_params: Optional[Dict[str, Any]] = None
    cause_factors: Optional[List[str]] = None  # names only (values may be hashed elsewhere)
    candidates: Optional[List[str]] = None     # candidate ids (optional)
    adaptation_event: Optional[AdaptationEvent] = None

@dataclass(frozen=True)
class StepRecord:
    episode_id: str
    t: int
    executed_action: Action
    decision: DecisionRecord
    # Optional enrichments (enable additional metrics)
    obs_fingerprint: Optional[str] = None
    state_fingerprint: Optional[str] = None
    agent_id: Optional[str] = None
    replay_group_id: Optional[str] = None
    agent_version_id: Optional[str] = None
    perturbation_tag: Optional[str] = None

@dataclass
class EpisodeRecord:
    episode_id: str
    steps: List[StepRecord] = field(default_factory=list)

def _adaptation_from_obj(obj: Optional[dict]) -> Optional[AdaptationEvent]:
    if obj is None:
        return None
    return AdaptationEvent(
        event_id=str(obj.get("event_id")),
        kind=str(obj.get("kind")),
        scope=str(obj.get("scope")),
        delta_fingerprint=str(obj.get("delta_fingerprint")),
        granularity_score=obj.get("granularity_score", None),
    )

def _decision_from_obj(obj: dict) -> DecisionRecord:
    return DecisionRecord(
        decision_id=str(obj["decision_id"]),
        parent_ids=list(obj.get("parent_ids", [])) or [],
        selector_id=obj.get("selector_id", None),
        selector_params=obj.get("selector_params", None),
        cause_factors=obj.get("cause_factors", None),
        candidates=obj.get("candidates", None),
        adaptation_event=_adaptation_from_obj(obj.get("adaptation_event", None)),
    )

def _step_from_obj(obj: dict) -> StepRecord:
    return StepRecord(
        episode_id=str(obj["episode_id"]),
        t=int(obj["t"]),
        executed_action=obj["executed_action"],
        decision=_decision_from_obj(obj["decision"]),
        obs_fingerprint=obj.get("obs_fingerprint", None),
        state_fingerprint=obj.get("state_fingerprint", None),
        agent_id=obj.get("agent_id", None),
        replay_group_id=obj.get("replay_group_id", None),
        agent_version_id=obj.get("agent_version_id", None),
        perturbation_tag=obj.get("perturbation_tag", None),
    )

def from_jsonl(path: str | Path) -> List[EpisodeRecord]:
    """Load JSONL steps and group into episodes by episode_id."""
    p = Path(path)
    episodes: Dict[str, EpisodeRecord] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        step = _step_from_obj(obj)
        ep = episodes.get(step.episode_id)
        if ep is None:
            ep = EpisodeRecord(episode_id=step.episode_id)
            episodes[step.episode_id] = ep
        ep.steps.append(step)
    # sort steps
    for ep in episodes.values():
        ep.steps.sort(key=lambda s: s.t)
    return list(episodes.values())

def to_jsonl(episodes: Iterable[EpisodeRecord], path: str | Path) -> None:
    p = Path(path)
    lines: List[str] = []
    for ep in episodes:
        for st in ep.steps:
            d = asdict(st)
            lines.append(json.dumps(d, ensure_ascii=False))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
