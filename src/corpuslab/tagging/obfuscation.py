"""Detectors for obfuscation tags: whitespace_obfuscation, non_ascii, high_entropy."""

from __future__ import annotations

import re
from typing import List

from corpuslab.constants import DEFAULT_HIGH_ENTROPY_THRESHOLD
from corpuslab.models import TagName, TagResult
from corpuslab.tagging.base import BaseDetector
from corpuslab.tagging.confidence import clamp, ratio_to_confidence, shannon_entropy

_UNUSUAL_WHITESPACE = re.compile(r"[\t\v\f\r\x00\x0b\x0c\x85\xa0\u2000-\u200f\u2028\u2029\u202f\u205f\u3000\ufeff]")
_MULTI_SPACE = re.compile(r"  +")


class WhitespaceObfuscationDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        unusual = _UNUSUAL_WHITESPACE.findall(raw)
        multi_space = _MULTI_SPACE.findall(raw)
        total_anomalies = len(unusual) + len(multi_space)
        if total_anomalies == 0:
            return []
        ratio = total_anomalies / len(raw) if raw else 0
        confidence = ratio_to_confidence(min(ratio * 20, 1.0), floor=0.3, ceil=0.9)
        return [TagResult(
            tag=TagName.WHITESPACE_OBFUSCATION,
            confidence=confidence,
            rationale=f"Found {len(unusual)} unusual whitespace chars and {len(multi_space)} multi-space runs",
            features={
                "unusual_whitespace_count": len(unusual),
                "multi_space_runs": len(multi_space),
            },
        )]


class NonAsciiDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        non_ascii = [c for c in raw if ord(c) > 127]
        if not non_ascii:
            return []
        ratio = len(non_ascii) / len(raw) if raw else 0
        confidence = ratio_to_confidence(min(ratio * 5, 1.0), floor=0.4, ceil=0.95)
        return [TagResult(
            tag=TagName.NON_ASCII,
            confidence=confidence,
            rationale=f"Found {len(non_ascii)} non-ASCII characters ({ratio:.1%} of payload)",
            features={
                "non_ascii_count": len(non_ascii),
                "non_ascii_ratio": round(ratio, 4),
            },
        )]


class HighEntropyDetector(BaseDetector):
    def __init__(self, threshold: float = DEFAULT_HIGH_ENTROPY_THRESHOLD):
        self.threshold = threshold

    def detect(self, raw: str) -> List[TagResult]:
        if len(raw) < 8:
            return []
        ent = shannon_entropy(raw)
        if ent < self.threshold:
            return []
        confidence = clamp((ent - self.threshold) / (8.0 - self.threshold) * 0.5 + 0.5)
        return [TagResult(
            tag=TagName.HIGH_ENTROPY,
            confidence=confidence,
            rationale=f"Shannon entropy {ent:.2f} exceeds threshold {self.threshold}",
            features={"entropy": round(ent, 4), "threshold": self.threshold},
        )]
