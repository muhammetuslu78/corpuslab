"""Detectors for heuristic tags: very_long_input, cleartext, multi_url_encoded."""

from __future__ import annotations

from typing import List
from urllib.parse import unquote

from corpuslab.constants import DEFAULT_VERY_LONG_THRESHOLD, MAX_URL_DECODE_DEPTH
from corpuslab.models import TagName, TagResult
from corpuslab.tagging.base import BaseDetector
from corpuslab.tagging.confidence import clamp


class VeryLongInputDetector(BaseDetector):
    def __init__(self, threshold: int = DEFAULT_VERY_LONG_THRESHOLD):
        self.threshold = threshold

    def detect(self, raw: str) -> List[TagResult]:
        if len(raw) < self.threshold:
            return []
        ratio = len(raw) / self.threshold
        confidence = clamp(0.7 + min(ratio - 1, 3) * 0.1)
        return [TagResult(
            tag=TagName.VERY_LONG_INPUT,
            confidence=confidence,
            rationale=f"Payload length {len(raw)} exceeds threshold {self.threshold}",
            features={"length": len(raw), "threshold": self.threshold},
        )]


class CleartextDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        if not raw:
            return []
        # Check all printable ASCII
        is_printable = all(32 <= ord(c) <= 126 or c in "\n\r\t" for c in raw)
        if not is_printable:
            return []
        # Check no encoding markers
        encoding_markers = ["%", "&#", "\\u", "\\x", "\\U"]
        has_markers = any(m in raw for m in encoding_markers)
        if has_markers:
            return []
        return [TagResult(
            tag=TagName.CLEARTEXT,
            confidence=0.9,
            rationale="All printable ASCII, no encoding markers detected",
            features={"length": len(raw), "is_ascii": True},
        )]


class MultiUrlEncodedDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        current = raw
        depth = 0
        for _ in range(MAX_URL_DECODE_DEPTH):
            decoded = unquote(current)
            if decoded == current:
                break
            current = decoded
            depth += 1
        if depth < 2:
            return []
        confidence = clamp(0.6 + depth * 0.1)
        return [TagResult(
            tag=TagName.MULTI_URL_ENCODED,
            confidence=confidence,
            rationale=f"URL-decoding converged after {depth} rounds",
            features={"decode_depth": depth},
        )]
