"""Tests for ingestion engine."""

from corpuslab.ingest.engine import build_record, ingest_stream
from corpuslab.models import IngestMetadata


class TestBuildRecord:
    def test_builds_complete_record(self):
        meta = IngestMetadata(source_file="test.txt", source_format="text", line_number=1)
        record = build_record("hello world", meta)

        assert record.id  # non-empty
        assert record.raw == "hello world"
        assert record.raw_length == 11
        assert record.fingerprints is not None
        assert len(record.canonical_views) == 4
        assert record.ingest_meta.source_file == "test.txt"

    def test_deterministic_id(self):
        meta = IngestMetadata(source_format="text")
        r1 = build_record("test", meta)
        r2 = build_record("test", meta)
        assert r1.id == r2.id


class TestIngestStream:
    def test_text_ingest(self, sample_text_path):
        records = list(ingest_stream(sample_text_path, "text"))
        assert len(records) > 0
        for r in records:
            assert r.id
            assert r.fingerprints is not None

    def test_csv_ingest(self, sample_csv_path):
        records = list(ingest_stream(sample_csv_path, "csv", field="payload"))
        assert len(records) == 5

    def test_json_ingest(self, sample_json_path):
        records = list(ingest_stream(sample_json_path, "json", field="payload"))
        assert len(records) == 5

    def test_jsonl_ingest(self, sample_jsonl_path):
        records = list(ingest_stream(sample_jsonl_path, "jsonl", field="payload"))
        assert len(records) == 5

    def test_auto_detect(self, sample_text_path):
        records = list(ingest_stream(sample_text_path, "auto"))
        assert len(records) > 0

    def test_with_redaction(self, sample_text_path):
        records = list(ingest_stream(sample_text_path, "text", redact=True))
        # Records with emails should have redacted_raw
        for r in records:
            if "user@example.com" in r.raw:
                assert r.redacted_raw is not None
                assert "user@example.com" not in r.redacted_raw
