"""Tests for encoding detectors."""

import pytest

from corpuslab.models import TagName
from corpuslab.tagging.encoding import (
    Base64Detector,
    HtmlEntityDetector,
    UnicodeEscapeDetector,
    UrlEncodedDetector,
)


class TestUrlEncodedDetector:
    det = UrlEncodedDetector()

    @pytest.mark.parametrize("payload,expected_min_conf", [
        ("%3Cscript%3Ealert(1)%3C/script%3E", 0.5),
        ("%3Cimg%20src%3Dx%3E", 0.5),
        ("foo%20bar%20baz", 0.4),
    ])
    def test_positive(self, payload, expected_min_conf):
        results = self.det.detect(payload)
        assert len(results) == 1
        assert results[0].tag == TagName.URL_ENCODED
        assert results[0].confidence >= expected_min_conf

    @pytest.mark.parametrize("payload", [
        "hello world",
        "no encoding here",
        "",
    ])
    def test_negative(self, payload):
        results = self.det.detect(payload)
        assert len(results) == 0


class TestBase64Detector:
    det = Base64Detector()

    @pytest.mark.parametrize("payload", [
        "dGhpcyBpcyBhIHRlc3QgcGF5bG9hZCBmb3IgYmFzZTY0IGRldGVjdGlvbg==",
        "SGVsbG8gV29ybGQgdGhpcyBpcyBhIHRlc3Q=",
    ])
    def test_positive(self, payload):
        results = self.det.detect(payload)
        assert len(results) == 1
        assert results[0].tag == TagName.BASE64_LIKE

    @pytest.mark.parametrize("payload", [
        "hello world",
        "short",
        "",
    ])
    def test_negative(self, payload):
        results = self.det.detect(payload)
        assert len(results) == 0


class TestHtmlEntityDetector:
    det = HtmlEntityDetector()

    @pytest.mark.parametrize("payload,expected_min_conf", [
        ("&lt;script&gt;alert(1)&lt;/script&gt;", 0.5),
        ("&#60;img&#62;", 0.4),
        ("&#x3C;div&#x3E;", 0.4),
    ])
    def test_positive(self, payload, expected_min_conf):
        results = self.det.detect(payload)
        assert len(results) == 1
        assert results[0].tag == TagName.HTML_ENTITIES
        assert results[0].confidence >= expected_min_conf

    def test_negative(self):
        results = self.det.detect("hello world")
        assert len(results) == 0


class TestUnicodeEscapeDetector:
    det = UnicodeEscapeDetector()

    @pytest.mark.parametrize("payload", [
        "\\u003Cscript\\u003E",
        "\\x3Cimg\\x20src\\x3Dx\\x3E",
    ])
    def test_positive(self, payload):
        results = self.det.detect(payload)
        assert len(results) == 1
        assert results[0].tag == TagName.UNICODE_ESCAPES

    def test_negative(self):
        results = self.det.detect("hello world")
        assert len(results) == 0
