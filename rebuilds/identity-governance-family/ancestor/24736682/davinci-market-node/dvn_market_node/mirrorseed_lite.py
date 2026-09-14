from __future__ import annotations

from typing import Any, Dict, List, Tuple


def mirrorseed_integrity(report: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Lite contradiction checks.

    clear/warn/break based on structural contradictions only.
    """
    issues: List[str] = []

    mm = report.get("mythmath", {})
    coh = float(mm.get("coherence", 0.0))
    fi = float(mm.get("fragility_index", 0.0))

    if not (0.0 <= coh <= 1.0):
        issues.append("coherence_out_of_range")
    if not (0.0 <= fi <= 1.0):
        issues.append("fragility_out_of_range")

    if report.get("non_operable") is True and report.get("intents"):
        issues.append("non_operable_but_intents_present")

    if issues:
        return ("warn", issues)

    return ("clear", [])
