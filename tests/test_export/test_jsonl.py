"""Tests for JSONL export."""

from corpuslab.export.jsonl import export_jsonl
from corpuslab.ingest.engine import build_record
from corpuslab.models import IngestMetadata
from corpuslab.storage.corpus import iterate_corpus


class TestJsonlExport:
    def test_roundtrip(self, tmp_path):
        meta = IngestMetadata(source_format="text")
        records = [build_record("hello", meta), build_record("world", meta)]
        path = str(tmp_path / "export.jsonl")

        count = export_jsonl(iter(records), path)
        assert count == 2

        read_back = list(iterate_corpus(path))
        assert len(read_back) == 2
        assert read_back[0].raw == "hello"
