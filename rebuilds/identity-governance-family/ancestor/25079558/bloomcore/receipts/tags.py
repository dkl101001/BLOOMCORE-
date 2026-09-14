# ============================================================
# BLOOMCORE — Receipt Tag Normalizer (Glyph-safe)
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List, Optional

# Canonical tag charset:
#   - upper A-Z 0-9
#   - separators: . _ - : /
_TAG_RE = re.compile(r"^[A-Z0-9][A-Z0-9._\-:/]{0,127}$")

# Minimal Greek → Latin transliteration for stability of tags.
_GREEK_MAP = {
    "Α":"A","Β":"B","Γ":"G","Δ":"D","Ε":"E","Ζ":"Z","Η":"E","Θ":"TH",
    "Ι":"I","Κ":"K","Λ":"L","Μ":"M","Ν":"N","Ξ":"X","Ο":"O","Π":"P",
    "Ρ":"R","Σ":"S","Τ":"T","Υ":"Y","Φ":"PH","Χ":"CH","Ψ":"PS","Ω":"O",
    "ά":"A","έ":"E","ή":"E","ί":"I","ό":"O","ύ":"Y","ώ":"O",
    "α":"A","β":"B","γ":"G","δ":"D","ε":"E","ζ":"Z","η":"E","θ":"TH",
    "ι":"I","κ":"K","λ":"L","μ":"M","ν":"N","ξ":"X","ο":"O","π":"P",
    "ρ":"R","σ":"S","ς":"S","τ":"T","υ":"Y","φ":"PH","χ":"CH","ψ":"PS","ω":"O",
}

def _strip_diacritics(s: str) -> str:
    # NFKD decomposes diacritics; remove combining marks.
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def _greek_to_latin(s: str) -> str:
    return "".join(_GREEK_MAP.get(ch, ch) for ch in s)

def normalize_tag(tag: str) -> str:
    """Normalize a single tag into canonical, drift-resistant form.

    Examples:
      - "Σοφύρ"  -> "SOPHYR"
      - "Sophýr" -> "SOPHYR"
      - "mode:explore" -> "MODE:EXPLORE"
      - "RECEIPT.RUN.START.v1" preserved (uppercased, separators preserved)
    """
    if not isinstance(tag, str):
        raise TypeError("tag must be a string")

    t = " ".join(tag.strip().split())
    if not t:
        raise ValueError("empty tag")

    # Preserve structural separators but normalize glyph/diacritics.
    t = _strip_diacritics(t)
    t = _greek_to_latin(t)

    # Uppercase for canonical tags.
    t = t.upper()

    # Replace spaces with underscore
    t = t.replace(" ", "_")

    # Collapse repeated separators (keep hyphen/dot/underscore)
    t = re.sub(r"__+", "_", t)

    # Remove characters outside our allowed set by mapping to underscore,
    # but keep separators . _ - : /
    t = re.sub(r"[^A-Z0-9._\-:/]", "_", t)

    # Trim underscores at ends (but keep leading letter/digit requirement)
    t = t.strip("_")
    if not t:
        raise ValueError("tag normalized to empty")

    if not _TAG_RE.match(t):
        raise ValueError(f"tag not canonical after normalization: {t!r}")
    return t

def normalize_tags(tags: Optional[Iterable[str]]) -> List[str]:
    """Normalize, deduplicate, and sort tags for stable hashing."""
    if tags is None:
        return []
    out = [normalize_tag(t) for t in tags]
    return sorted(set(out))

def validate_tags(tags: Iterable[str]) -> None:
    for t in tags:
        if not isinstance(t, str):
            raise TypeError("tag must be string")
        if not _TAG_RE.match(t):
            raise ValueError(f"tag violates canonical charset: {t!r}")
