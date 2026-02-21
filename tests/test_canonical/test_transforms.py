"""Tests for canonical transforms."""

from corpuslab.canonical.transforms import (
    html_unescape,
    nfkc_normalize,
    url_decode_deep,
    url_decode_single,
)


class TestUrlDecode:
    def test_single(self):
        assert url_decode_single("%3Cscript%3E") == "<script>"

    def test_noop(self):
        assert url_decode_single("hello") == "hello"

    def test_deep_multi(self):
        from urllib.parse import quote
        double = quote(quote("<test>"))
        assert url_decode_deep(double) == "<test>"

    def test_deep_single(self):
        assert url_decode_deep("%3C") == "<"


class TestHtmlUnescape:
    def test_named(self):
        assert html_unescape("&lt;script&gt;") == "<script>"

    def test_numeric(self):
        assert html_unescape("&#60;") == "<"

    def test_hex(self):
        assert html_unescape("&#x3C;") == "<"

    def test_noop(self):
        assert html_unescape("hello") == "hello"


class TestNfkcNormalize:
    def test_normalize(self):
        # NFKC normalizes compatibility characters
        assert nfkc_normalize("\uff21") == "A"  # Fullwidth A

    def test_noop(self):
        assert nfkc_normalize("hello") == "hello"
