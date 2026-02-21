"""Detector registry for running all tag detectors."""

from __future__ import annotations

from typing import List

from corpuslab.models import TagResult
from corpuslab.tagging.base import BaseDetector
from corpuslab.tagging.encoding import (
    Base64Detector,
    HtmlEntityDetector,
    UnicodeEscapeDetector,
    UrlEncodedDetector,
)
from corpuslab.tagging.heuristics import (
    CleartextDetector,
    MultiUrlEncodedDetector,
    VeryLongInputDetector,
)
from corpuslab.tagging.obfuscation import (
    HighEntropyDetector,
    NonAsciiDetector,
    WhitespaceObfuscationDetector,
)
from corpuslab.tagging.structure import JsonEscapedDetector, MixedEncodingDetector

_DETECTORS: List[BaseDetector] = []
_mixed_detector = MixedEncodingDetector()
_initialized = False


def _init_registry() -> None:
    global _initialized
    if _initialized:
        return
    for cls in [
        UrlEncodedDetector,
        Base64Detector,
        HtmlEntityDetector,
        UnicodeEscapeDetector,
        JsonEscapedDetector,
        WhitespaceObfuscationDetector,
        NonAsciiDetector,
        HighEntropyDetector,
        VeryLongInputDetector,
        CleartextDetector,
        MultiUrlEncodedDetector,
    ]:
        _DETECTORS.append(cls())
    _initialized = True


def run_all_detectors(raw: str) -> List[TagResult]:
    """Run all registered detectors on the raw payload."""
    _init_registry()
    results: List[TagResult] = []
    for det in _DETECTORS:
        results.extend(det.detect(raw))
    # Run mixed encoding detector with existing results
    results.extend(_mixed_detector.detect_from_tags(results))
    return results
