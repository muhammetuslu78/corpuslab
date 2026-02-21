"""Tests for CSV export."""

import csv

from corpuslab.export.csv_export import export_csv
from corpuslab.ingest.engine import build_record
from corpuslab.models import IngestMetadata


class TestCsvExport:
    def test_export(self, tmp_path):
        meta = IngestMetadata(source_format="text")
        records = [build_record("hello", meta), build_record("world", meta)]
        path = str(tmp_path / "export.csv")

        count = export_csv(iter(records), path)
        assert count == 2

        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2

    def test_custom_fields(self, tmp_path):
        meta = IngestMetadata(source_format="text")
        records = [build_record("test", meta)]
        path = str(tmp_path / "export.csv")

        export_csv(iter(records), path, fields=["id", "raw_length"])
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert set(rows[0].keys()) == {"id", "raw_length"}
