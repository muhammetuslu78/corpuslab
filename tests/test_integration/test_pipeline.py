"""End-to-end integration tests."""

from corpuslab.export.csv_export import export_csv
from corpuslab.export.jsonl import export_jsonl
from corpuslab.export.markdown import export_markdown
from corpuslab.ingest.engine import ingest_stream
from corpuslab.storage.corpus import iterate_corpus, write_corpus


class TestFullPipeline:
    def test_ingest_to_export_roundtrip(self, sample_text_path, tmp_path):
        # Ingest
        records = list(ingest_stream(sample_text_path, "text"))
        assert len(records) > 0

        # Every record must have all fields
        for r in records:
            assert r.id
            assert r.raw
            assert r.raw_length > 0
            assert r.fingerprints is not None
            assert len(r.canonical_views) == 4
            assert isinstance(r.tags, list)

        # Write corpus
        corpus_path = str(tmp_path / "corpus.jsonl")
        write_corpus(corpus_path, iter(records))

        # Read back and verify roundtrip
        read_back = list(iterate_corpus(corpus_path))
        assert len(read_back) == len(records)
        for orig, back in zip(records, read_back):
            assert orig.id == back.id
            assert orig.raw == back.raw
            assert orig.fingerprints == back.fingerprints

        # Export to CSV
        csv_path = str(tmp_path / "export.csv")
        export_csv(iterate_corpus(corpus_path), csv_path)

        # Export to Markdown
        md_path = str(tmp_path / "report.md")
        export_markdown(iterate_corpus(corpus_path), md_path)

    def test_deterministic_output(self, sample_text_path, tmp_path):
        """Same input + same config = identical output."""
        path1 = str(tmp_path / "corpus1.jsonl")
        path2 = str(tmp_path / "corpus2.jsonl")

        records1 = list(ingest_stream(sample_text_path, "text"))
        records2 = list(ingest_stream(sample_text_path, "text"))

        # Same records, same order, same fingerprints
        assert len(records1) == len(records2)
        for r1, r2 in zip(records1, records2):
            assert r1.id == r2.id
            assert r1.fingerprints == r2.fingerprints
            assert len(r1.tags) == len(r2.tags)

    def test_all_formats(self, sample_text_path, sample_csv_path, sample_json_path, sample_jsonl_path):
        """Verify all input formats produce valid records."""
        for path, fmt, field in [
            (sample_text_path, "text", None),
            (sample_csv_path, "csv", "payload"),
            (sample_json_path, "json", "payload"),
            (sample_jsonl_path, "jsonl", "payload"),
        ]:
            records = list(ingest_stream(path, fmt, field))
            assert len(records) > 0, f"No records from {fmt}"
            for r in records:
                assert r.fingerprints is not None, f"Missing fingerprints in {fmt}"
