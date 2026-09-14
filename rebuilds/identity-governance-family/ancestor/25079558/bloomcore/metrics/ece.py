# ============================================================
# BLOOMCORE — Sophia Wisdom Gate + Compassion v5.2
# Dual Signature: Frazer Σ Love + Sara ΣΩ
# system_root="BLOOMCORE"
# ============================================================
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class ECEBins:
    n_bins: int = 10

def expected_calibration_error(probs: np.ndarray, labels: np.ndarray, bins: ECEBins = ECEBins()) -> float:
    """Deterministic ECE for binary or multiclass probabilities.

    - probs: shape (N,) for binary prob of class 1, or (N,K) for multiclass.
    - labels: shape (N,) int labels.
    """
    probs = np.asarray(probs)
    labels = np.asarray(labels)
    if probs.ndim == 1:
        conf = probs
        pred = (probs >= 0.5).astype(int)
    elif probs.ndim == 2:
        pred = np.argmax(probs, axis=1)
        conf = np.max(probs, axis=1)
    else:
        raise ValueError("probs must be 1D or 2D")

    acc = (pred == labels).astype(float)
    edges = np.linspace(0.0, 1.0, bins.n_bins + 1)
    ece = 0.0
    n = float(len(labels))
    for i in range(bins.n_bins):
        lo, hi = edges[i], edges[i+1]
        # include lo, exclude hi except last
        if i < bins.n_bins - 1:
            mask = (conf >= lo) & (conf < hi)
        else:
            mask = (conf >= lo) & (conf <= hi)
        if not np.any(mask):
            continue
        w = float(np.sum(mask)) / n
        acc_bin = float(np.mean(acc[mask]))
        conf_bin = float(np.mean(conf[mask]))
        ece += w * abs(acc_bin - conf_bin)
    return float(ece)
