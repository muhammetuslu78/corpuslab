"""Tests for obfuscation detectors."""

import pytest

from corpuslab.models import TagName
from corpuslab.tagging.obfuscation import (
    HighEntropyDetector,
    NonAsciiDetector,
    WhitespaceObfuscationDetector,
)


class TestWhitespaceObfuscationDetector:
    det = WhitespaceObfuscationDetector()

    def test_tabs(self):
        results = self.det.detect("test\tcontent\twith\ttabs")
        assert len(results) == 1
        assert results[0].tag == TagName.WHITESPACE_OBFUSCATION

    def test_multi_space(self):
        results = self.det.detect("multiple   spaces   here")
        assert len(results) == 1

    def test_normal_text(self):
        assert self.det.detect("normal text") == []


class TestNonAsciiDetector:
    det = NonAsciiDetector()

    def test_positive(self):
        results = self.det.detect("café naïve résumé")
        assert len(results) == 1
        assert results[0].tag == TagName.NON_ASCII

    def test_cjk(self):
        results = self.det.detect("你好世界")
        assert len(results) == 1

    def test_ascii_only(self):
        assert self.det.detect("hello world") == []


class TestHighEntropyDetector:
    det = HighEntropyDetector()

    def test_high_entropy(self):
        # Random-looking string
        results = self.det.detect("aB3$kL9@mN7#pQ2&rT5*vX8!")
        assert len(results) == 1
        assert results[0].tag == TagName.HIGH_ENTROPY

    def test_low_entropy(self):
        assert self.det.detect("aaaaaaaaaa") == []

    def test_short_string(self):
        assert self.det.detect("abc") == []
