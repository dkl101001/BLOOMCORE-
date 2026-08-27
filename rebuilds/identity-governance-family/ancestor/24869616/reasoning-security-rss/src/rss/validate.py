from __future__ import annotations

from typing import List, Dict, Tuple, Optional
from .schema import EpisodeRecord

def validate_episodes(episodes: List[EpisodeRecord]) -> List[str]:
    errors: List[str] = []
    decision_ids: Dict[str, Tuple[str, int]] = {}

    for ep in episodes:
        if not ep.episode_id:
            errors.append("episode_id missing")
        last_t: Optional[int] = None
        for st in ep.steps:
            if st.episode_id != ep.episode_id:
                errors.append(f"episode mismatch: ep={ep.episode_id} step={st.episode_id}")
            if last_t is not None and st.t < last_t:
                errors.append(f"non-monotonic t in episode {ep.episode_id}: {st.t} after {last_t}")
            last_t = st.t

            dr = st.decision
            if not dr.decision_id:
                errors.append(f"missing decision_id in episode {ep.episode_id} t={st.t}")
            else:
                if dr.decision_id in decision_ids:
                    prev_ep, prev_t = decision_ids[dr.decision_id]
                    errors.append(
                        f"duplicate decision_id {dr.decision_id}: "
                        f"{prev_ep}:{prev_t} and {ep.episode_id}:{st.t}"
                    )
                decision_ids[dr.decision_id] = (ep.episode_id, st.t)

            # Required minimal fields
            if st.executed_action is None:
                errors.append(f"missing executed_action in {ep.episode_id} t={st.t}")
            if dr.parent_ids is None:
                errors.append(f"parent_ids must be list in {ep.episode_id} t={st.t}")

            # Light type checks
            if dr.cause_factors is not None and not isinstance(dr.cause_factors, list):
                errors.append(f"cause_factors must be list or null in {ep.episode_id} t={st.t}")

    # lineage link existence (parent_ids)
    all_ids = set(decision_ids.keys())
    for ep in episodes:
        for st in ep.steps:
            for pid in st.decision.parent_ids:
                if pid and pid not in all_ids:
                    errors.append(
                        f"missing parent decision_id {pid} referenced by {st.decision.decision_id}"
                    )

    return errors
