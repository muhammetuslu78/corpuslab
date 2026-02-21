"""Detectors for structural tags: json_escaped, mixed_encoding."""

from __future__ import annotations

import re
from typing import List

from corpuslab.models import TagName, TagResult
from corpuslab.tagging.base import BaseDetector
from corpuslab.tagging.confidence import ratio_to_confidence

_JSON_ESCAPE_PATTERN = re.compile(r'\\["\\/bfnrt]|\\u[0-9A-Fa-f]{4}')


class JsonEscapedDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        matches = _JSON_ESCAPE_PATTERN.findall(raw)
        if not matches:
            return []
        ratio = len(matches) / len(raw) if raw else 0
        confidence = ratio_to_confidence(min(ratio * 15, 1.0), floor=0.3, ceil=0.9)
        return [TagResult(
            tag=TagName.JSON_ESCAPED,
            confidence=confidence,
            rationale=f"Found {len(matches)} JSON escape sequences",
            features={"escape_count": len(matches), "sample_escapes": matches[:5]},
        )]


class MixedEncodingDetector(BaseDetector):
    """Flags payloads that have 2+ encoding tags above threshold."""

    ENCODING_TAGS = {
        TagName.URL_ENCODED,
        TagName.HTML_ENTITIES,
        TagName.UNICODE_ESCAPES,
        TagName.JSON_ESCAPED,
        TagName.BASE64_LIKE,
    }

    def detect_from_tags(self, existing_tags: List[TagResult]) -> List[TagResult]:
        encoding_hits = [
            t for t in existing_tags
            if t.tag in self.ENCODING_TAGS and t.confidence >= 0.4
        ]
        if len(encoding_hits) < 2:
            return []
        tag_names = [t.tag.value for t in encoding_hits]
        avg_conf = sum(t.confidence for t in encoding_hits) / len(encoding_hits)
        return [TagResult(
            tag=TagName.MIXED_ENCODING,
            confidence=min(avg_conf + 0.1, 1.0),
            rationale=f"Multiple encoding types detected: {', '.join(tag_names)}",
            features={"encoding_types": tag_names, "encoding_count": len(encoding_hits)},
        )]

    def detect(self, raw: str) -> List[TagResult]:
        # This detector needs other tag results; handled in registry
        return []
