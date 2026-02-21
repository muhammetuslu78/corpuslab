"""Confidence scoring utilities."""

from __future__ import annotations

import math
from collections import Counter


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value between lo and hi."""
    return max(lo, min(hi, val))


def ratio_to_confidence(ratio: float, floor: float = 0.3, ceil: float = 0.95) -> float:
    """Map a 0-1 ratio to a confidence score within [floor, ceil]."""
    return clamp(floor + ratio * (ceil - floor))


def shannon_entropy(data: str) -> float:
    """Compute Shannon entropy over character distribution."""
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy
