"""Tests for format detection."""

from corpuslab.ingest.detect import detect_format


class TestDetectFormat:
    def test_txt_extension(self, sample_text_path):
        assert detect_format(sample_text_path) == "text"

    def test_csv_extension(self, sample_csv_path):
        assert detect_format(sample_csv_path) == "csv"

    def test_json_extension(self, sample_json_path):
        assert detect_format(sample_json_path) == "json"

    def test_jsonl_extension(self, sample_jsonl_path):
        assert detect_format(sample_jsonl_path) == "jsonl"
