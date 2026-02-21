"""Tests for structure detectors."""

from corpuslab.models import TagName, TagResult
from corpuslab.tagging.structure import JsonEscapedDetector, MixedEncodingDetector


class TestJsonEscapedDetector:
    det = JsonEscapedDetector()

    def test_positive(self):
        results = self.det.detect('{"key": "value with \\"quotes\\" and \\n newlines"}')
        assert len(results) == 1
        assert results[0].tag == TagName.JSON_ESCAPED

    def test_negative(self):
        assert self.det.detect("hello world") == []


class TestMixedEncodingDetector:
    det = MixedEncodingDetector()

    def test_positive(self):
        tags = [
            TagResult(tag=TagName.URL_ENCODED, confidence=0.7, rationale="test"),
            TagResult(tag=TagName.HTML_ENTITIES, confidence=0.6, rationale="test"),
        ]
        results = self.det.detect_from_tags(tags)
        assert len(results) == 1
        assert results[0].tag == TagName.MIXED_ENCODING

    def test_negative_single(self):
        tags = [TagResult(tag=TagName.URL_ENCODED, confidence=0.7, rationale="test")]
        results = self.det.detect_from_tags(tags)
        assert results == []

    def test_negative_low_confidence(self):
        tags = [
            TagResult(tag=TagName.URL_ENCODED, confidence=0.2, rationale="test"),
            TagResult(tag=TagName.HTML_ENTITIES, confidence=0.1, rationale="test"),
        ]
        results = self.det.detect_from_tags(tags)
        assert results == []
