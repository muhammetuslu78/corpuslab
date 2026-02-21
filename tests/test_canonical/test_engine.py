"""Tests for canonical engine."""

from corpuslab.canonical.engine import compute_canonical_views


class TestCanonicalEngine:
    def test_produces_four_views(self):
        views = compute_canonical_views("hello")
        assert len(views) == 4
        names = {v.name for v in views}
        assert names == {"url_decoded", "url_decoded_deep", "html_decoded", "nfkc_normalized"}

    def test_url_decoded_view(self):
        views = compute_canonical_views("%3Cscript%3E")
        url_view = next(v for v in views if v.name == "url_decoded")
        assert url_view.value == "<script>"
        assert len(url_view.trace) == 1
        assert url_view.trace[0].changed is True

    def test_nfkc_view_chain(self):
        views = compute_canonical_views("%3Cscript%3E")
        nfkc_view = next(v for v in views if v.name == "nfkc_normalized")
        assert len(nfkc_view.trace) == 3  # url_decode, html_unescape, nfkc

    def test_no_change_traces(self):
        views = compute_canonical_views("hello")
        for view in views:
            for step in view.trace:
                assert step.changed is False
