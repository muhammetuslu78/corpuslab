"""Detectors for encoding-related tags: url_encoded, base64_like, html_entities, unicode_escapes."""

from __future__ import annotations

import base64
import re
from typing import List
from urllib.parse import unquote

from corpuslab.constants import BASE64_MIN_LENGTH, BASE64_PADDING_BONUS, URL_ENCODED_MIN_RATIO
from corpuslab.models import TagName, TagResult
from corpuslab.tagging.base import BaseDetector
from corpuslab.tagging.confidence import clamp, ratio_to_confidence

_PERCENT_PATTERN = re.compile(r"%[0-9A-Fa-f]{2}")
_HTML_ENTITY_NAMED = re.compile(r"&[a-zA-Z]{2,8};")
_HTML_ENTITY_NUMERIC = re.compile(r"&#[0-9]{1,7};")
_HTML_ENTITY_HEX = re.compile(r"&#x[0-9A-Fa-f]{1,6};")
_UNICODE_ESCAPE_U = re.compile(r"\\u[0-9A-Fa-f]{4}")
_UNICODE_ESCAPE_X = re.compile(r"\\x[0-9A-Fa-f]{2}")
_UNICODE_ESCAPE_BIG_U = re.compile(r"\\U[0-9A-Fa-f]{8}")
_BASE64_PATTERN = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")
_BASE64_URL_PATTERN = re.compile(r"[A-Za-z0-9_-]{20,}")


class UrlEncodedDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        matches = _PERCENT_PATTERN.findall(raw)
        if not matches:
            return []
        count = len(matches)
        encoded_chars = count * 3
        ratio = encoded_chars / len(raw) if raw else 0
        if ratio < URL_ENCODED_MIN_RATIO:
            return []
        decoded = unquote(raw)
        changed = decoded != raw
        if not changed:
            return []
        confidence = ratio_to_confidence(ratio, floor=0.4, ceil=0.95)
        return [TagResult(
            tag=TagName.URL_ENCODED,
            confidence=confidence,
            rationale=f"Found {count} percent-encoded tokens ({ratio:.1%} of payload)",
            features={"percent_encoded_count": count, "percent_encoded_ratio": round(ratio, 4)},
        )]


class Base64Detector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        results: List[TagResult] = []
        for pattern in (_BASE64_PATTERN, _BASE64_URL_PATTERN):
            for m in pattern.finditer(raw):
                candidate = m.group()
                if len(candidate) < BASE64_MIN_LENGTH:
                    continue
                try:
                    padded = candidate + "=" * (4 - len(candidate) % 4) if len(candidate) % 4 else candidate
                    decoded = base64.b64decode(padded, validate=True)
                    decoded.decode("utf-8", errors="strict")
                except Exception:
                    try:
                        padded = candidate + "=" * (4 - len(candidate) % 4) if len(candidate) % 4 else candidate
                        base64.b64decode(padded, validate=True)
                    except Exception:
                        continue
                confidence = clamp(0.5 + len(candidate) / 200)
                if candidate.endswith("="):
                    confidence = clamp(confidence + BASE64_PADDING_BONUS)
                results.append(TagResult(
                    tag=TagName.BASE64_LIKE,
                    confidence=confidence,
                    rationale=f"Found base64-like segment of length {len(candidate)}",
                    features={"segment_length": len(candidate), "has_padding": candidate.endswith("=")},
                ))
                return results  # Return on first valid match to avoid duplicates
        return results


class HtmlEntityDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        named = _HTML_ENTITY_NAMED.findall(raw)
        numeric = _HTML_ENTITY_NUMERIC.findall(raw)
        hexed = _HTML_ENTITY_HEX.findall(raw)
        total = len(named) + len(numeric) + len(hexed)
        if total == 0:
            return []
        ratio = total / len(raw) if raw else 0
        confidence = ratio_to_confidence(min(ratio * 10, 1.0), floor=0.4, ceil=0.95)
        features = {}
        if named:
            features["named_entities"] = named[:10]
        if numeric:
            features["numeric_entities"] = numeric[:10]
        if hexed:
            features["hex_entities"] = hexed[:10]
        return [TagResult(
            tag=TagName.HTML_ENTITIES,
            confidence=confidence,
            rationale=f"Found {total} HTML entities (named={len(named)}, numeric={len(numeric)}, hex={len(hexed)})",
            features=features,
        )]


class UnicodeEscapeDetector(BaseDetector):
    def detect(self, raw: str) -> List[TagResult]:
        u_matches = _UNICODE_ESCAPE_U.findall(raw)
        x_matches = _UNICODE_ESCAPE_X.findall(raw)
        big_u_matches = _UNICODE_ESCAPE_BIG_U.findall(raw)
        total = len(u_matches) + len(x_matches) + len(big_u_matches)
        if total == 0:
            return []
        ratio = total / len(raw) if raw else 0
        confidence = ratio_to_confidence(min(ratio * 15, 1.0), floor=0.4, ceil=0.95)
        return [TagResult(
            tag=TagName.UNICODE_ESCAPES,
            confidence=confidence,
            rationale=f"Found {total} unicode escape sequences (\\uXXXX={len(u_matches)}, \\xNN={len(x_matches)}, \\UXXXXXXXX={len(big_u_matches)})",
            features={
                "u_escape_count": len(u_matches),
                "x_escape_count": len(x_matches),
                "big_u_escape_count": len(big_u_matches),
            },
        )]
