from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..signals import RegimeState
from ..receipts.simple import receipt
from .compendium_state import read_compendium_claim, write_compendium_claim
from .memory_state import read_memory, write_memory
from .models import ResolvedState, SourceClaim, StateKey, stable_hash
from .receipt_state import latest_state_step


def _parse_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


@dataclass
class StateOrchestrator:
    """Tri-source state carry: Compendium + Receipts + Engine Memory.

    This is an OSS-grade prior-art standard: mutual calibration + drift protection.
    """

    receipts_path: Path

    def resolve(self, *, compendium_state: Dict[str, Any], key: StateKey, target_eq_id: Optional[str]) -> Tuple[ResolvedState, List[Dict[str, Any]]]:
        """Resolve prev_state from memory, compendium, receipts, and emit reconcile receipts.

        Returns (resolved_state, reconcile_receipts).
        """
        claims: List[SourceClaim] = []
        drift_reasons: List[str] = []

        # Memory claim
        mem = read_memory(key)
        if isinstance(mem, dict):
            claims.append(SourceClaim("memory", mem.get("as_of_eq_id"), mem.get("prev_state"), dict(mem)))
        else:
            claims.append(SourceClaim("memory", None, None, {}))

        # Compendium claim
        comp_claim = read_compendium_claim(compendium_state, key)
        if isinstance(comp_claim, dict):
            claims.append(SourceClaim("compendium", comp_claim.get("as_of_eq_id"), comp_claim.get("prev_state"), dict(comp_claim)))
        else:
            claims.append(SourceClaim("compendium", None, None, {}))

        # Receipts claim (authoritative spine if present)
        r = latest_state_step(self.receipts_path, key)
        if isinstance(r, dict):
            claims.append(SourceClaim("receipts", r.get("as_of_eq_id"), r.get("prev_state"), dict(r)))
        else:
            claims.append(SourceClaim("receipts", None, None, {}))

        # Choose authority: prefer receipts; else compendium; else memory; else NEUTRAL
        chosen_src = "receipts"
        chosen_payload: Dict[str, Any] = {}
        if r:
            chosen_payload = r
        elif comp_claim:
            chosen_src = "compendium"
            chosen_payload = comp_claim
        elif mem:
            chosen_src = "memory"
            chosen_payload = mem
        else:
            chosen_src = "none"
            chosen_payload = {}

        prev_state: RegimeState = str(chosen_payload.get("prev_state") or "STATE_NEUTRAL")  # type: ignore
        as_of_eq_id = chosen_payload.get("as_of_eq_id")
        inv = _parse_float(chosen_payload.get("invalidation_level"))
        intensity = float(chosen_payload.get("last_intensity", chosen_payload.get("intensity", 0.0)) or 0.0)
        reason = str(chosen_payload.get("last_reason", chosen_payload.get("reason", "")) or "")
        receipt_tip = None
        if r and r.get("event_id"):
            receipt_tip = str(r.get("event_id"))
        comp_hash = compendium_state.get("compendium_state_hash")
        if not comp_hash:
            comp_hash = stable_hash(compendium_state)
            compendium_state["compendium_state_hash"] = comp_hash

        # Drift detection: disagreements across sources for the same (or latest-known) state.
        seen_states = {}
        for c in claims:
            if c.prev_state is None:
                continue
            seen_states[c.src] = c.prev_state

        if len(set(seen_states.values())) > 1:
            drift_reasons.append(f"prev_state disagreement: {seen_states}")

        # If compendium claims newer than receipts, mark WARN (unanchored)
        if comp_claim and r:
            try:
                if str(comp_claim.get("as_of_eq_id", "")) > str(r.get("as_of_eq_id", "")):
                    drift_reasons.append("compendium_newer_than_receipts")
            except Exception:
                pass

        # If memory disagrees with both compendium and receipts, mark WARN
        if mem and ((comp_claim and mem.get("prev_state") != comp_claim.get("prev_state")) and (r and mem.get("prev_state") != r.get("prev_state"))):
            drift_reasons.append("memory_disagrees_with_compendium_and_receipts")

        drift_status = "OK"
        if drift_reasons:
            drift_status = "WARN"
        if "compendium_newer_than_receipts" in drift_reasons:
            drift_status = "BREAK"

        resolved = ResolvedState(
            state_key=key,
            as_of_eq_id=as_of_eq_id,
            prev_state=prev_state,
            invalidation_level=inv,
            last_intensity=float(intensity),
            last_reason=reason,
            receipt_tip_event_id=receipt_tip,
            compendium_hash=str(comp_hash) if comp_hash else None,
            drift_status=drift_status,  # type: ignore
            drift_reasons=drift_reasons,
            claims=claims,
        )

        # Repair memory immediately from resolved
        write_memory(key, {
            "state_key": key.to_str(),
            "as_of_eq_id": resolved.as_of_eq_id,
            "prev_state": resolved.prev_state,
            "invalidation_level": resolved.invalidation_level,
            "last_intensity": resolved.last_intensity,
            "last_reason": resolved.last_reason,
        })

        recs: List[Dict[str, Any]] = []
        recs.append(receipt("STATE.RECONCILE.v1", {
            "eq_id": target_eq_id,
            "state_key": key.to_str(),
            "chosen_src": chosen_src,
            "resolved": resolved.to_dict(),
        }))
        if drift_status != "OK":
            recs.append(receipt("STATE.DRIFT.v1", {
                "eq_id": target_eq_id,
                "state_key": key.to_str(),
                "status": drift_status,
                "reasons": drift_reasons,
                "claims": [
                    {"src": c.src, "as_of_eq_id": c.as_of_eq_id, "prev_state": c.prev_state}
                    for c in claims
                ],
            }))

        return (resolved, recs)

    def commit(
        self,
        *,
        compendium_state: Dict[str, Any],
        key: StateKey,
        eq_id: str,
        prev_state: RegimeState,
        new_state: RegimeState,
        intensity: float,
        reason: str,
        invalidation_level: Optional[float],
        receipt_tip_event_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Commit new state to receipts + compendium state dict + memory.

        Returns receipts to be appended.
        """
        step_payload: Dict[str, Any] = {
            "eq_id": eq_id,
            "state_key": key.to_str(),
            "as_of_eq_id": eq_id,
            "prev_state": prev_state,
            "new_state": new_state,
            "intensity": float(intensity),
            "reason": reason,
            "invalidation_level": invalidation_level,
            "receipt_tip_event_id": receipt_tip_event_id,
        }

        step = receipt("STATE.STEP.v1", step_payload)

        # Update in-memory cache
        write_memory(key, {
            "state_key": key.to_str(),
            "as_of_eq_id": eq_id,
            "prev_state": new_state,
            "invalidation_level": invalidation_level,
            "last_intensity": float(intensity),
            "last_reason": reason,
            "receipt_tip_event_id": step.get("event_id"),
        })

        # Update compendium state claim (will be persisted by engine)
        claim = {
            "as_of_eq_id": eq_id,
            "prev_state": new_state,
            "invalidation_level": invalidation_level,
            "last_intensity": float(intensity),
            "last_reason": reason,
            "receipt_tip_event_id": step.get("event_id"),
        }
        write_compendium_claim(compendium_state, key, claim)

        snap = receipt("STATE.SNAPSHOT.v1", {
            "eq_id": eq_id,
            "state_key": key.to_str(),
            "compendium_state_hash": compendium_state.get("compendium_state_hash"),
            "receipt_tip_event_id": step.get("event_id"),
        })

        return [step, snap]
