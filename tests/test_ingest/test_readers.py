"""Tests for format-specific readers."""

from corpuslab.ingest.readers import read_csv, read_json_array, read_jsonl, read_text_lines


class TestTextReader:
    def test_reads_lines(self, sample_text_path):
        results = list(read_text_lines(sample_text_path))
        assert len(results) > 0
        for payload, meta in results:
            assert isinstance(payload, str)
            assert payload.strip() != ""
            assert "line_number" in meta


class TestCsvReader:
    def test_reads_payload_field(self, sample_csv_path):
        results = list(read_csv(sample_csv_path, "payload"))
        assert len(results) == 5
        assert results[0][0] == "hello world"

    def test_default_first_column(self, sample_csv_path):
        results = list(read_csv(sample_csv_path))
        assert len(results) == 5


class TestJsonReader:
    def test_reads_array(self, sample_json_path):
        results = list(read_json_array(sample_json_path, "payload"))
        assert len(results) == 5

    def test_extracts_field(self, sample_json_path):
        results = list(read_json_array(sample_json_path, "payload"))
        assert results[0][0] == "hello world"


class TestJsonlReader:
    def test_reads_lines(self, sample_jsonl_path):
        results = list(read_jsonl(sample_jsonl_path, "payload"))
        assert len(results) == 5

    def test_extracts_payload(self, sample_jsonl_path):
        results = list(read_jsonl(sample_jsonl_path, "payload"))
        assert results[0][0] == "hello world"
