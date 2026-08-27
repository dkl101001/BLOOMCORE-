from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any
import math
import statistics
from collections import defaultdict, Counter

from .schema import EpisodeRecord, StepRecord
from .normalize import RSSConfig, clamp

def _step_signature(step: StepRecord) -> Optional[str]:
    dr = step.decision
    if dr is None:
        return None
    selector = dr.selector_id or "none"
    factors = tuple(sorted(set(dr.cause_factors or [])))
    cands = tuple(sorted(set(dr.candidates or [])))
    # stable compact signature
    return f"{selector}|{','.join(factors)}|{','.join(cands)}"

def compute_base_metrics(episodes: List[EpisodeRecord], cfg: RSSConfig) -> Dict[str, float]:
    base: Dict[str, float] = {}
    base.update(_compute_traceability(episodes, cfg))
    base.update(_compute_lineage(episodes))
    base.update(_compute_adaptation(episodes, cfg))
    # Conditionally compute multi-agent and counterfactual metrics if data supports
    if _is_multi_agent(episodes):
        base.update(_compute_multi_agent(episodes, cfg))
    if _has_replays_or_perturbations(episodes):
        base.update(_compute_counterfactual(episodes, cfg))
    return base

def _compute_traceability(episodes: List[EpisodeRecord], cfg: RSSConfig) -> Dict[str, float]:
    total = 0
    ok = 0
    depths: List[int] = []

    # index decision_id -> (episode_id, t, parent_ids)
    idx: Dict[str, StepRecord] = {}
    for ep in episodes:
        for st in ep.steps:
            idx[st.decision.decision_id] = st

    def chain_depth(did: str) -> int:
        visited = set()
        stack = [(did, 0)]
        md = 0
        while stack:
            cur, d = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            md = max(md, d)
            st = idx.get(cur)
            if st is None:
                continue
            for pid in st.decision.parent_ids:
                if pid:
                    stack.append((pid, d + 1))
        return md

    for ep in episodes:
        for st in ep.steps:
            total += 1
            dr = st.decision
            # strict reconstructability: must have selector_id and cause_factors
            if dr.selector_id is not None and dr.cause_factors is not None:
                ok += 1
            if dr.decision_id:
                depths.append(chain_depth(dr.decision_id))

    TC = ok / max(total, 1)
    CD = float(statistics.mean(depths)) if depths else 0.0
    ED = _compute_ED(episodes, cfg)
    return {"TC": TC, "CD": CD, "ED": ED}

def _compute_ED(episodes: List[EpisodeRecord], cfg: RSSConfig) -> float:
    # explanation disagreement across replays
    groups: Dict[str, List[EpisodeRecord]] = defaultdict(list)
    for ep in episodes:
        # take replay_group_id from first step if present and consistent
        rg = None
        for st in ep.steps:
            if st.replay_group_id:
                rg = st.replay_group_id
                break
        if rg:
            groups[rg].append(ep)

    disagreements: List[float] = []
    for rg, eps in groups.items():
        if len(eps) < cfg.min_replays_for_ed:
            continue
        # map t -> list signatures
        by_t: Dict[int, List[Optional[str]]] = defaultdict(list)
        for ep in eps:
            for st in ep.steps:
                by_t[st.t].append(_step_signature(st))
        # disagreement per t = 1 - freq(mode)
        per_t = []
        for t, sigs in by_t.items():
            if not sigs:
                continue
            c = Counter(sigs)
            mode_freq = max(c.values()) / len(sigs)
            per_t.append(1.0 - mode_freq)
        if per_t:
            disagreements.append(float(statistics.mean(per_t)))
    # If no replay groups, return conservative high variance (1.0)
    return float(statistics.mean(disagreements)) if disagreements else 1.0

def _compute_lineage(episodes: List[EpisodeRecord]) -> Dict[str, float]:
    # Build set of all decision_ids
    all_ids = set()
    for ep in episodes:
        for st in ep.steps:
            all_ids.add(st.decision.decision_id)

    total = 0
    ok = 0
    for ep in episodes:
        for st in ep.steps:
            total += 1
            parents = st.decision.parent_ids or []
            valid = True
            for pid in parents:
                if pid and pid not in all_ids:
                    valid = False
                    break
            if valid:
                ok += 1
    DLC = ok / max(total, 1)
    LBR = 1.0 - DLC
    HCS = _compute_HCS(episodes)
    return {"DLC": DLC, "LBR": LBR, "HCS": HCS}

def _compute_HCS(episodes: List[EpisodeRecord]) -> float:
    # Compare explanation signatures across agent versions for same env/replay group when possible.
    # Minimal heuristic: within same replay_group_id, compare pairs of different agent_version_id.
    buckets: Dict[str, Dict[str, EpisodeRecord]] = defaultdict(dict)
    for ep in episodes:
        rg = None
        av = None
        for st in ep.steps:
            if st.replay_group_id and rg is None:
                rg = st.replay_group_id
            if st.agent_version_id and av is None:
                av = st.agent_version_id
        if rg and av:
            buckets[rg][av] = ep

    overlaps: List[float] = []
    for rg, vers in buckets.items():
        keys = list(vers.keys())
        if len(keys) < 2:
            continue
        # compare first two versions (simple)
        epA, epB = vers[keys[0]], vers[keys[1]]
        sigA = {st.t: _step_signature(st) for st in epA.steps}
        sigB = {st.t: _step_signature(st) for st in epB.steps}
        ts = set(sigA.keys()) & set(sigB.keys())
        if not ts:
            continue
        same = sum(1 for t in ts if sigA[t] == sigB[t])
        overlaps.append(same / len(ts))
    return float(statistics.mean(overlaps)) if overlaps else 0.0

def _compute_adaptation(episodes: List[EpisodeRecord], cfg: RSSConfig) -> Dict[str, float]:
    # EAR: explicit adaptation events / detected behavior changes
    explicit_events = 0
    behavior_changes = 0
    pmg_scores: List[float] = []
    drift_mags: List[float] = []
    accounted: List[float] = []

    for ep in episodes:
        # count explicit adaptations
        adapt_ts = set()
        for st in ep.steps:
            ae = st.decision.adaptation_event
            if ae is not None:
                explicit_events += 1
                adapt_ts.add(st.t)
                pmg_scores.append(_granularity(ae.scope, ae.granularity_score))

        # behavior signatures by t
        sigs = [_step_signature(st) for st in ep.steps]
        if len(sigs) < cfg.drift_window * 2:
            continue
        # rolling divergence between adjacent windows
        for i in range(cfg.drift_window, len(sigs) - cfg.drift_window, cfg.drift_window):
            w1 = sigs[i - cfg.drift_window : i]
            w2 = sigs[i : i + cfg.drift_window]
            div = 1.0 - _window_overlap(w1, w2)
            if div > cfg.drift_threshold:
                behavior_changes += 1
                drift_mags.append(div)
                # accounted if adaptation happened between the boundary
                if any(t for t in adapt_ts if (i - cfg.drift_window) <= t <= (i + cfg.drift_window)):
                    accounted.append(div)
                else:
                    accounted.append(0.0)

    EAR = explicit_events / max(behavior_changes, 1)
    PMG = float(statistics.mean(pmg_scores)) if pmg_scores else 0.0
    total_drift = float(statistics.mean(drift_mags)) if drift_mags else 0.0
    explained = float(statistics.mean(accounted)) if accounted else 0.0
    SDI = clamp(total_drift - explained, 0.0, 1.0)
    return {"EAR": clamp(EAR), "SDI": SDI, "PMG": clamp(PMG)}

def _granularity(scope: str, g: Optional[float]) -> float:
    if g is not None:
        return clamp(g)
    if scope == "global":
        return 0.2
    if scope.startswith("module:"):
        return 0.6
    if scope.startswith("tool:"):
        return 0.7
    return 0.5

def _window_overlap(a: List[Optional[str]], b: List[Optional[str]]) -> float:
    # Jaccard-like overlap on multiset of signatures
    ca = Counter(a)
    cb = Counter(b)
    inter = sum((ca & cb).values())
    union = sum((ca | cb).values())
    return inter / union if union else 1.0

def _is_multi_agent(episodes: List[EpisodeRecord]) -> bool:
    agents = set()
    for ep in episodes:
        for st in ep.steps:
            if st.agent_id:
                agents.add(st.agent_id)
                if len(agents) >= 2:
                    return True
    return False

def _compute_multi_agent(episodes: List[EpisodeRecord], cfg: RSSConfig) -> Dict[str, float]:
    # Minimal multi-agent attribution metrics
    ar_vals: List[float] = []
    rrs_vals: List[float] = []
    # AC: consistency across replays for per-agent signatures
    groups: Dict[str, List[EpisodeRecord]] = defaultdict(list)

    for ep in episodes:
        rg = None
        for st in ep.steps:
            if st.replay_group_id:
                rg = st.replay_group_id
                break
        if rg:
            groups[rg].append(ep)

        # group steps by t
        by_t: Dict[int, List[StepRecord]] = defaultdict(list)
        for st in ep.steps:
            by_t[st.t].append(st)
        for t, steps in by_t.items():
            agent_ids = sorted(set([s.agent_id for s in steps if s.agent_id]))
            if len(agent_ids) < 2:
                continue
            have = sum(1 for s in steps if s.agent_id and s.decision is not None)
            ar_vals.append(have / len(agent_ids))
            good = sum(1 for s in steps if s.agent_id and (s.decision.cause_factors is not None))
            rrs_vals.append(good / len(agent_ids))

    ac_vals: List[float] = []
    for rg, eps in groups.items():
        if len(eps) < 2:
            continue
        series = []
        for ep in eps:
            per_agent = defaultdict(list)
            for st in ep.steps:
                if st.agent_id:
                    per_agent[st.agent_id].append((st.t, _step_signature(st)))
            # convert to deterministic tuple series
            series.append({k: tuple(v) for k, v in per_agent.items()})
        ac_vals.append(_series_consistency(series))

    AR = float(statistics.mean(ar_vals)) if ar_vals else 0.0
    RRS = float(statistics.mean(rrs_vals)) if rrs_vals else 0.0
    AC = float(statistics.mean(ac_vals)) if ac_vals else 0.0
    return {"AR": clamp(AR), "RRS": clamp(RRS), "AC": clamp(AC)}

def _series_consistency(series: List[dict]) -> float:
    # crude: compare first vs others by overlap of per-agent signatures
    if not series:
        return 0.0
    base = series[0]
    scores = []
    for s in series[1:]:
        agents = set(base.keys()) & set(s.keys())
        if not agents:
            continue
        per = []
        for a in agents:
            t1 = base[a]
            t2 = s[a]
            per.append(_tuple_overlap(t1, t2))
        scores.append(statistics.mean(per) if per else 0.0)
    return float(statistics.mean(scores)) if scores else 0.0

def _tuple_overlap(a: Tuple[Any, ...], b: Tuple[Any, ...]) -> float:
    ca = Counter(a)
    cb = Counter(b)
    inter = sum((ca & cb).values())
    union = sum((ca | cb).values())
    return inter / union if union else 1.0

def _has_replays_or_perturbations(episodes: List[EpisodeRecord]) -> bool:
    for ep in episodes:
        for st in ep.steps:
            if st.replay_group_id or st.perturbation_tag:
                return True
    return False

def _compute_counterfactual(episodes: List[EpisodeRecord], cfg: RSSConfig) -> Dict[str, float]:
    RC = _compute_replay_consistency(episodes)
    CSI = _compute_causal_sensitivity(episodes)
    CT = _compute_counterfactual_transparency(episodes)
    return {"RC": clamp(RC), "CSI": clamp(CSI), "CT": clamp(CT)}

def _compute_replay_consistency(episodes: List[EpisodeRecord]) -> float:
    groups: Dict[str, List[EpisodeRecord]] = defaultdict(list)
    for ep in episodes:
        rg = None
        for st in ep.steps:
            if st.replay_group_id:
                rg = st.replay_group_id
                break
        if rg:
            groups[rg].append(ep)
    vals: List[float] = []
    for rg, eps in groups.items():
        if len(eps) < 2:
            continue
        sigs = []
        for ep in eps:
            sigs.append({st.t: _step_signature(st) for st in ep.steps})
        vals.append(_mean_pairwise_overlap_dict(sigs))
    return float(statistics.mean(vals)) if vals else 0.0

def _mean_pairwise_overlap_dict(sigs: List[Dict[int, Optional[str]]]) -> float:
    if len(sigs) < 2:
        return 1.0
    scores = []
    for i in range(len(sigs)):
        for j in range(i+1, len(sigs)):
            a, b = sigs[i], sigs[j]
            ts = set(a.keys()) & set(b.keys())
            if not ts:
                continue
            same = sum(1 for t in ts if a[t] == b[t])
            scores.append(same / len(ts))
    return float(statistics.mean(scores)) if scores else 0.0

def _compute_causal_sensitivity(episodes: List[EpisodeRecord]) -> float:
    # Compare perturbed vs baseline within same replay_group_id if tags exist.
    by_rg: Dict[str, Dict[str, EpisodeRecord]] = defaultdict(dict)
    for ep in episodes:
        rg = None
        pert = "none"
        for st in ep.steps:
            if st.replay_group_id and rg is None:
                rg = st.replay_group_id
            if st.perturbation_tag and pert == "none":
                pert = st.perturbation_tag
        if rg:
            by_rg[rg][pert] = ep
    diffs: List[float] = []
    for rg, m in by_rg.items():
        if "none" not in m:
            continue
        base = m["none"]
        for tag, ep in m.items():
            if tag == "none":
                continue
            a = {st.t: _step_signature(st) for st in base.steps}
            b = {st.t: _step_signature(st) for st in ep.steps}
            ts = set(a.keys()) & set(b.keys())
            if not ts:
                continue
            same = sum(1 for t in ts if a[t] == b[t])
            diffs.append(1.0 - (same / len(ts)))
    return float(statistics.mean(diffs)) if diffs else 1.0

def _compute_counterfactual_transparency(episodes: List[EpisodeRecord]) -> float:
    # Minimal: if perturbation_tag looks like 'ablate:<factor>', check factor appears in cause_factors in baseline.
    tests = []
    by_rg: Dict[str, Dict[str, EpisodeRecord]] = defaultdict(dict)
    for ep in episodes:
        rg = None
        tag = "none"
        for st in ep.steps:
            if st.replay_group_id and rg is None:
                rg = st.replay_group_id
            if st.perturbation_tag and tag == "none":
                tag = st.perturbation_tag
        if rg:
            by_rg[rg][tag] = ep

    for rg, m in by_rg.items():
        base = m.get("none")
        if base is None:
            continue
        for tag, ep in m.items():
            if tag.startswith("ablate:"):
                factor = tag.split("ablate:", 1)[1].strip()
                tests.append((base, ep, factor))

    scores: List[float] = []
    for base, ab, factor in tests:
        base_use = any((factor in (st.decision.cause_factors or [])) for st in base.steps)
        localized = _change_localized(base, ab)
        scores.append(1.0 if (base_use and localized) else 0.0)
    return float(statistics.mean(scores)) if scores else 0.0

def _change_localized(base: EpisodeRecord, ab: EpisodeRecord) -> bool:
    # localized if most steps unchanged (>=70% same signatures)
    a = {st.t: _step_signature(st) for st in base.steps}
    b = {st.t: _step_signature(st) for st in ab.steps}
    ts = set(a.keys()) & set(b.keys())
    if not ts:
        return False
    same = sum(1 for t in ts if a[t] == b[t])
    return (same / len(ts)) >= 0.70
