"""Tests for Markdown report export."""

from corpuslab.export.markdown import export_markdown
from corpuslab.ingest.engine import build_record
from corpuslab.models import IngestMetadata


class TestMarkdownExport:
    def test_generates_report(self, tmp_path):
        meta = IngestMetadata(source_file="test.txt", source_format="text")
        records = [build_record("hello", meta), build_record("%3Cscript%3E", meta)]
        path = str(tmp_path / "report.md")

        count = export_markdown(iter(records), path)
        assert count == 2

        with open(path) as f:
            content = f.read()
        assert "# CorpusLab Analysis Report" in content
        assert "Tag Distribution" in content
        assert "Run Manifest" in content

    def test_empty_report(self, tmp_path):
        path = str(tmp_path / "report.md")
        count = export_markdown(iter([]), path)
        assert count == 0
