"""Tests for heuristic detectors."""

from corpuslab.models import TagName
from corpuslab.tagging.heuristics import (
    CleartextDetector,
    MultiUrlEncodedDetector,
    VeryLongInputDetector,
)


class TestVeryLongInputDetector:
    det = VeryLongInputDetector()

    def test_long(self):
        results = self.det.detect("A" * 2000)
        assert len(results) == 1
        assert results[0].tag == TagName.VERY_LONG_INPUT

    def test_short(self):
        assert self.det.detect("short") == []


class TestCleartextDetector:
    det = CleartextDetector()

    def test_cleartext(self):
        results = self.det.detect("hello world simple test")
        assert len(results) == 1
        assert results[0].tag == TagName.CLEARTEXT

    def test_has_encoding(self):
        assert self.det.detect("%3Cscript%3E") == []

    def test_non_ascii(self):
        assert self.det.detect("café") == []


class TestMultiUrlEncodedDetector:
    det = MultiUrlEncodedDetector()

    def test_double_encoded(self):
        from urllib.parse import quote
        payload = quote(quote("<script>alert(1)</script>"))
        results = self.det.detect(payload)
        assert len(results) == 1
        assert results[0].tag == TagName.MULTI_URL_ENCODED
        assert results[0].features["decode_depth"] >= 2

    def test_single_encoded(self):
        from urllib.parse import quote
        assert self.det.detect(quote("hello")) == []
