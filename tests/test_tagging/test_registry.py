"""Tests for detector registry."""

from corpuslab.tagging.registry import run_all_detectors


class TestRegistry:
    def test_cleartext_detection(self):
        results = run_all_detectors("hello world")
        tag_names = {r.tag.value for r in results}
        assert "cleartext" in tag_names

    def test_url_encoded_detection(self):
        results = run_all_detectors("%3Cscript%3Ealert(1)%3C/script%3E")
        tag_names = {r.tag.value for r in results}
        assert "url_encoded" in tag_names

    def test_returns_list(self):
        results = run_all_detectors("")
        assert isinstance(results, list)

    def test_all_results_have_confidence(self):
        results = run_all_detectors("%3Cscript%3Ealert(1)%3C/script%3E")
        for r in results:
            assert 0.0 <= r.confidence <= 1.0
