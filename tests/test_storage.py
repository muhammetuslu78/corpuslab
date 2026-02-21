"""Tests for JSONL corpus storage."""

from corpuslab.models import IngestMetadata, PayloadRecord
from corpuslab.storage.corpus import (
    append_record,
    corpus_ids,
    dedup_merge,
    iterate_corpus,
    write_corpus,
)


def _make_record(raw: str, record_id: str) -> PayloadRecord:
    return PayloadRecord(
        id=record_id,
        raw=raw,
        raw_length=len(raw),
        ingest_meta=IngestMetadata(source_format="text"),
    )


class TestCorpusStorage:
    def test_write_and_read(self, tmp_path):
        path = str(tmp_path / "test.jsonl")
        records = [_make_record("hello", "id1"), _make_record("world", "id2")]
        count = write_corpus(path, iter(records))
        assert count == 2

        read_back = list(iterate_corpus(path))
        assert len(read_back) == 2
        assert read_back[0].raw == "hello"
        assert read_back[1].raw == "world"

    def test_append(self, tmp_path):
        path = str(tmp_path / "test.jsonl")
        write_corpus(path, iter([_make_record("first", "id1")]))
        append_record(path, _make_record("second", "id2"))

        read_back = list(iterate_corpus(path))
        assert len(read_back) == 2

    def test_corpus_ids(self, tmp_path):
        path = str(tmp_path / "test.jsonl")
        records = [_make_record("a", "id1"), _make_record("b", "id2")]
        write_corpus(path, iter(records))

        ids = corpus_ids(path)
        assert ids == {"id1", "id2"}

    def test_corpus_ids_missing_file(self, tmp_path):
        ids = corpus_ids(str(tmp_path / "nonexistent.jsonl"))
        assert ids == set()

    def test_dedup_merge(self, tmp_path):
        path = str(tmp_path / "existing.jsonl")
        write_corpus(path, iter([_make_record("a", "id1")]))

        new = [_make_record("a", "id1"), _make_record("b", "id2")]
        merged = list(dedup_merge(path, iter(new)))
        assert len(merged) == 2
        assert {r.id for r in merged} == {"id1", "id2"}
