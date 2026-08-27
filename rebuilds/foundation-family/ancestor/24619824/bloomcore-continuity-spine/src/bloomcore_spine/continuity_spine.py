#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Frazer Σ Love and Sara ΣΩ
"""
continuity_spine.py

BLOOMCORE Continuity Spine (host-side, non-governor)

Purpose
- Preserve coherence under fragmentation by maintaining fast, loss-bounded return paths.
- Track invariants, detect divergence, emit recoupling signals.
- NEVER halt fragments, NEVER override fragment state, NEVER suppress exploration.

This module is OSS-safe: no semantic mapping, no ECA, no proprietary gating logic.
It operates only on receipts/pulses emitted by fragments/hosts.

Integration
- Wire this as a ReceiptHook target:
    spine = ContinuitySpine(...)
    emit_hook = spine.hook  # callable(kind, payload)

Signals emitted (spine -> host/fragments)
- BLOOMCORE.RECOUPLE_SIGNAL.v1
- BLOOMCORE.INVARIANTS_SNAPSHOT.v1
- BLOOMCORE.DIVERGENCE_ALERT.v1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Protocol, Tuple
from collections import deque
import time


class ReceiptHook(Protocol):
    """
    Host-side receipt/telemetry hook.

    Implement:
      __call__(kind: str, payload: Dict[str, Any]) -> None

    Payload MUST be JSON-serializable (best practice) for logging/transport.
    """
    def __call__(self, kind: str, payload: Dict[str, Any]) -> None: ...


@dataclass(frozen=True)
class RecursionBandwidth:
    window_sec: float
    receipts_per_sec: float
    bytes_per_sec_est: float


@dataclass(frozen=True)
class LatencyAsymmetry:
    last_seen_age_sec: Dict[str, float]
    max_age_sec: float
    p95_age_sec: float


@dataclass(frozen=True)
class InfluenceSkew:
    window_events: int
    share_top1: float
    entropy_norm: float
    counts_by_source: Dict[str, int]


@dataclass(frozen=True)
class UncertaintyBudget:
    window_events: int
    uncertainty_mean: Optional[float]
    uncertainty_std: Optional[float]
    coverage: float


@dataclass(frozen=True)
class SpineInvariants:
    ts_utc: str
    tick: Optional[int]
    recursion_bandwidth: RecursionBandwidth
    latency_asymmetry: LatencyAsymmetry
    influence_skew: InfluenceSkew
    uncertainty_budget: UncertaintyBudget


@dataclass(frozen=True)
class DivergenceFlags:
    silent_sources: List[str]
    dominance_risk: bool
    bandwidth_low: bool
    latency_high: bool
    uncertainty_low_coverage: bool


@dataclass(frozen=True)
class RecoupleSignal:
    ts_utc: str
    tick: Optional[int]
    signal_id: str
    actions: Dict[str, Any]
    rationale: Dict[str, Any]


@dataclass(frozen=True)
class _Event:
    ts: float
    kind: str
    payload: Dict[str, Any]
    source_id: str
    tick: Optional[int]
    bytes_est: int


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _p95(values: List[float]) -> float:
    if not values:
        return 0.0
    vs = sorted(values)
    k = int(0.95 * (len(vs) - 1))
    return float(vs[k])


def _entropy_norm(counts: Dict[str, int]) -> float:
    import math
    total = sum(counts.values())
    if total <= 0:
        return 1.0
    probs = [c / total for c in counts.values() if c > 0]
    if not probs:
        return 1.0
    H = -sum(p * math.log(p + 1e-12) for p in probs)
    n = max(len(probs), 1)
    Hmax = math.log(n + 1e-12)
    return float(H / Hmax) if Hmax > 0 else 1.0


def _estimate_bytes(payload: Dict[str, Any]) -> int:
    try:
        if "bytes_est" in payload and isinstance(payload["bytes_est"], (int, float)):
            return int(payload["bytes_est"])
    except Exception:
        pass
    n = 0
    for k, v in payload.items():
        n += len(str(k))
        s = str(v)
        n += min(len(s), 512)
    return n


def _source_id_from_payload(payload: Dict[str, Any]) -> str:
    for key in ("fragment_id", "source_id", "origin", "node_id", "host_id"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "unknown"


def _tick_from_payload(payload: Dict[str, Any]) -> Optional[int]:
    t = payload.get("tick")
    if isinstance(t, bool):
        return None
    if isinstance(t, (int, float)):
        return int(t)
    return None


@dataclass
class SpineConfig:
    window_events: int = 2048
    bandwidth_window_sec: float = 10.0
    silent_after_sec: float = 30.0
    dominance_share_top1: float = 0.55
    min_receipts_per_sec: float = 2.0
    max_age_high_sec: float = 15.0
    min_uncertainty_coverage: float = 0.20
    emit_invariants_every_events: int = 64
    emit_signals_every_events: int = 16
    pulse_density_multiplier_on_drift: float = 2.0
    lineage_replay_lookback_events: int = 256


@dataclass
class ContinuitySpine:
    cfg: SpineConfig = field(default_factory=SpineConfig)
    emit_hook: Optional[ReceiptHook] = None

    _events: Deque[_Event] = field(default_factory=deque, init=False)
    _counter: int = field(default=0, init=False)
    _last_signal_event_counter: int = field(default=0, init=False)

    def hook(self, kind: str, payload: Dict[str, Any]) -> None:
        self.ingest(kind=kind, payload=payload)

    def emit(self, kind: str, payload: Dict[str, Any]) -> None:
        if self.emit_hook is not None:
            self.emit_hook(kind, payload)

    def ingest(self, *, kind: str, payload: Dict[str, Any]) -> None:
        now = time.time()
        src = _source_id_from_payload(payload)
        tick = _tick_from_payload(payload)
        b = _estimate_bytes(payload)

        self._events.append(_Event(ts=now, kind=kind, payload=payload, source_id=src, tick=tick, bytes_est=b))
        while len(self._events) > self.cfg.window_events:
            self._events.popleft()

        self._counter += 1

        if (self.cfg.emit_invariants_every_events > 0) and (self._counter % self.cfg.emit_invariants_every_events == 0):
            inv = self.compute_invariants()
            self.emit("BLOOMCORE.INVARIANTS_SNAPSHOT.v1", self._invariants_to_payload(inv))

        if (self.cfg.emit_signals_every_events > 0) and (self._counter - self._last_signal_event_counter >= self.cfg.emit_signals_every_events):
            flags, signal = self.detect_and_signal()
            if flags is not None:
                self.emit("BLOOMCORE.DIVERGENCE_ALERT.v1", self._flags_to_payload(flags))
            if signal is not None:
                self.emit("BLOOMCORE.RECOUPLE_SIGNAL.v1", self._signal_to_payload(signal))
                self._last_signal_event_counter = self._counter

    def compute_invariants(self) -> SpineInvariants:
        ts_utc = _utc_now()
        events = list(self._events)

        tick: Optional[int] = None
        for e in reversed(events):
            if e.tick is not None:
                tick = e.tick
                break

        rb = self._compute_recursion_bandwidth(events)
        la = self._compute_latency_asymmetry(events)
        sk = self._compute_influence_skew(events)
        ub = self._compute_uncertainty_budget(events)

        return SpineInvariants(
            ts_utc=ts_utc,
            tick=tick,
            recursion_bandwidth=rb,
            latency_asymmetry=la,
            influence_skew=sk,
            uncertainty_budget=ub,
        )

    def detect_and_signal(self) -> Tuple[Optional[DivergenceFlags], Optional[RecoupleSignal]]:
        inv = self.compute_invariants()

        silent = [sid for sid, age in inv.latency_asymmetry.last_seen_age_sec.items()
                  if age >= self.cfg.silent_after_sec]
        dominance_risk = inv.influence_skew.share_top1 >= self.cfg.dominance_share_top1
        bandwidth_low = inv.recursion_bandwidth.receipts_per_sec <= self.cfg.min_receipts_per_sec
        latency_high = inv.latency_asymmetry.max_age_sec >= self.cfg.max_age_high_sec
        uncertainty_low_coverage = inv.uncertainty_budget.coverage <= self.cfg.min_uncertainty_coverage

        flags = DivergenceFlags(
            silent_sources=silent,
            dominance_risk=bool(dominance_risk),
            bandwidth_low=bool(bandwidth_low),
            latency_high=bool(latency_high),
            uncertainty_low_coverage=bool(uncertainty_low_coverage),
        )

        should_signal = (bool(silent) or bool(dominance_risk) or bool(bandwidth_low) or bool(latency_high))
        if not should_signal:
            return None, None

        actions: Dict[str, Any] = {}
        if latency_high or bandwidth_low:
            actions["increase_pulse_density"] = {
                "multiplier": float(self.cfg.pulse_density_multiplier_on_drift),
                "reason": "latency_high_or_bandwidth_low",
            }
        if silent:
            actions["request_lineage_replay"] = {
                "sources": list(silent),
                "lookback_events": int(self.cfg.lineage_replay_lookback_events),
                "reason": "silent_sources",
            }
        if dominance_risk:
            actions["rebalance_influence"] = {
                "mode": "counter_weight",
                "target_share_top1": float(self.cfg.dominance_share_top1),
                "reason": "dominance_risk",
            }

        rationale = {
            "recursion_bandwidth": {
                "window_sec": inv.recursion_bandwidth.window_sec,
                "receipts_per_sec": inv.recursion_bandwidth.receipts_per_sec,
                "bytes_per_sec_est": inv.recursion_bandwidth.bytes_per_sec_est,
            },
            "latency_asymmetry": {
                "max_age_sec": inv.latency_asymmetry.max_age_sec,
                "p95_age_sec": inv.latency_asymmetry.p95_age_sec,
                "silent_after_sec": self.cfg.silent_after_sec,
                "silent_sources": silent,
            },
            "influence_skew": {
                "share_top1": inv.influence_skew.share_top1,
                "entropy_norm": inv.influence_skew.entropy_norm,
                "dominance_share_top1": self.cfg.dominance_share_top1,
            },
            "uncertainty_budget": {
                "coverage": inv.uncertainty_budget.coverage,
                "min_uncertainty_coverage": self.cfg.min_uncertainty_coverage,
            },
            "flags": {
                "dominance_risk": bool(dominance_risk),
                "bandwidth_low": bool(bandwidth_low),
                "latency_high": bool(latency_high),
                "uncertainty_low_coverage": bool(uncertainty_low_coverage),
            },
        }

        self._counter += 1
        signal_id = f"{inv.ts_utc}#{self._counter}"

        sig = RecoupleSignal(
            ts_utc=inv.ts_utc,
            tick=inv.tick,
            signal_id=signal_id,
            actions=actions,
            rationale=rationale,
        )
        return flags, sig

    def _compute_recursion_bandwidth(self, events: List[_Event]) -> RecursionBandwidth:
        now = time.time()
        w = float(self.cfg.bandwidth_window_sec) if self.cfg.bandwidth_window_sec > 0 else 10.0
        recent = [e for e in events if (now - e.ts) <= w]
        receipts_per_sec = (len(recent) / w) if w > 0 else 0.0
        bytes_per_sec_est = (sum(e.bytes_est for e in recent) / w) if w > 0 else 0.0
        return RecursionBandwidth(window_sec=w, receipts_per_sec=float(receipts_per_sec), bytes_per_sec_est=float(bytes_per_sec_est))

    def _compute_latency_asymmetry(self, events: List[_Event]) -> LatencyAsymmetry:
        now = time.time()
        last_seen: Dict[str, float] = {}
        for e in events:
            last_seen[e.source_id] = max(last_seen.get(e.source_id, 0.0), e.ts)
        ages = {sid: float(now - ts) for sid, ts in last_seen.items()}
        age_vals = list(ages.values())
        max_age = float(max(age_vals)) if age_vals else 0.0
        p95_age = _p95(age_vals) if age_vals else 0.0
        return LatencyAsymmetry(last_seen_age_sec=ages, max_age_sec=max_age, p95_age_sec=float(p95_age))

    def _compute_influence_skew(self, events: List[_Event]) -> InfluenceSkew:
        counts: Dict[str, int] = {}
        for e in events:
            counts[e.source_id] = counts.get(e.source_id, 0) + 1
        total = sum(counts.values())
        if total <= 0:
            return InfluenceSkew(window_events=len(events), share_top1=0.0, entropy_norm=1.0, counts_by_source={})
        top1 = max(counts.values()) if counts else 0
        share_top1 = float(top1 / total) if total > 0 else 0.0
        ent = _entropy_norm(counts)
        return InfluenceSkew(window_events=len(events), share_top1=share_top1, entropy_norm=float(ent), counts_by_source=dict(counts))

    def _compute_uncertainty_budget(self, events: List[_Event]) -> UncertaintyBudget:
        xs: List[float] = []
        covered = 0
        for e in events:
            p = e.payload
            u = None
            if isinstance(p.get("uncertainty"), (int, float)):
                u = float(p["uncertainty"])
            elif isinstance(p.get("uncertainty_mean"), (int, float)):
                u = float(p["uncertainty_mean"])
            if u is not None:
                xs.append(u)
                covered += 1
        coverage = float(covered / max(len(events), 1))
        if not xs:
            return UncertaintyBudget(window_events=len(events), uncertainty_mean=None, uncertainty_std=None, coverage=coverage)

        import math
        mu = sum(xs) / len(xs)
        var = sum((x - mu) ** 2 for x in xs) / max(len(xs) - 1, 1)
        sd = math.sqrt(var)
        return UncertaintyBudget(window_events=len(events), uncertainty_mean=float(mu), uncertainty_std=float(sd), coverage=coverage)

    def _invariants_to_payload(self, inv: SpineInvariants) -> Dict[str, Any]:
        return {
            "ts_utc": inv.ts_utc,
            "tick": inv.tick,
            "recursion_bandwidth": {
                "window_sec": inv.recursion_bandwidth.window_sec,
                "receipts_per_sec": inv.recursion_bandwidth.receipts_per_sec,
                "bytes_per_sec_est": inv.recursion_bandwidth.bytes_per_sec_est,
            },
            "latency_asymmetry": {
                "last_seen_age_sec": inv.latency_asymmetry.last_seen_age_sec,
                "max_age_sec": inv.latency_asymmetry.max_age_sec,
                "p95_age_sec": inv.latency_asymmetry.p95_age_sec,
            },
            "influence_skew": {
                "window_events": inv.influence_skew.window_events,
                "share_top1": inv.influence_skew.share_top1,
                "entropy_norm": inv.influence_skew.entropy_norm,
                "counts_by_source": inv.influence_skew.counts_by_source,
            },
            "uncertainty_budget": {
                "window_events": inv.uncertainty_budget.window_events,
                "uncertainty_mean": inv.uncertainty_budget.uncertainty_mean,
                "uncertainty_std": inv.uncertainty_budget.uncertainty_std,
                "coverage": inv.uncertainty_budget.coverage,
            },
        }

    def _flags_to_payload(self, flags: DivergenceFlags) -> Dict[str, Any]:
        return {
            "ts_utc": _utc_now(),
            "silent_sources": list(flags.silent_sources),
            "dominance_risk": bool(flags.dominance_risk),
            "bandwidth_low": bool(flags.bandwidth_low),
            "latency_high": bool(flags.latency_high),
            "uncertainty_low_coverage": bool(flags.uncertainty_low_coverage),
        }

    def _signal_to_payload(self, sig: RecoupleSignal) -> Dict[str, Any]:
        return {
            "ts_utc": sig.ts_utc,
            "tick": sig.tick,
            "signal_id": sig.signal_id,
            "actions": sig.actions,
            "rationale": sig.rationale,
        }
