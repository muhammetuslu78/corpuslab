"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from corpuslab.models import (
    CanonicalView,
    Fingerprints,
    IngestMetadata,
    PayloadRecord,
    TagName,
    TagResult,
    TransformStep,
)


class TestTagResult:
    def test_valid_tag(self):
        t = TagResult(tag=TagName.URL_ENCODED, confidence=0.8, rationale="test")
        assert t.tag == TagName.URL_ENCODED
        assert t.confidence == 0.8

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            TagResult(tag=TagName.URL_ENCODED, confidence=1.5, rationale="test")
        with pytest.raises(ValidationError):
            TagResult(tag=TagName.URL_ENCODED, confidence=-0.1, rationale="test")

    def test_json_roundtrip(self):
        t = TagResult(
            tag=TagName.BASE64_LIKE, confidence=0.7,
            rationale="found base64", features={"length": 40},
        )
        json_str = t.model_dump_json()
        t2 = TagResult.model_validate_json(json_str)
        assert t == t2


class TestPayloadRecord:
    def test_minimal_record(self):
        r = PayloadRecord(
            id="abc123",
            raw="test",
            raw_length=4,
            ingest_meta=IngestMetadata(source_format="text"),
        )
        assert r.id == "abc123"
        assert r.raw_length == 4
        assert r.tags == []

    def test_json_roundtrip(self):
        r = PayloadRecord(
            id="hash123",
            raw="test payload",
            raw_length=12,
            tags=[TagResult(tag=TagName.CLEARTEXT, confidence=0.9, rationale="cleartext")],
            ingest_meta=IngestMetadata(source_file="test.txt", source_format="text"),
        )
        json_str = r.model_dump_json()
        r2 = PayloadRecord.model_validate_json(json_str)
        assert r2.id == r.id
        assert r2.raw == r.raw
        assert len(r2.tags) == 1
        assert r2.tags[0].tag == TagName.CLEARTEXT


class TestTagNameEnum:
    def test_all_tags_exist(self):
        expected = {
            "cleartext", "url_encoded", "multi_url_encoded", "html_entities",
            "unicode_escapes", "json_escaped", "base64_like", "mixed_encoding",
            "whitespace_obfuscation", "non_ascii", "high_entropy", "very_long_input",
        }
        actual = {t.value for t in TagName}
        assert actual == expected
