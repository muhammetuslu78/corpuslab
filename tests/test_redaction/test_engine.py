"""Tests for redaction engine."""

import re

from corpuslab.constants import REDACTION_PLACEHOLDER
from corpuslab.ingest.engine import build_record
from corpuslab.models import IngestMetadata
from corpuslab.redaction.engine import redact, redact_record


class TestRedact:
    def test_email(self):
        result = redact("contact user@example.com please")
        assert REDACTION_PLACEHOLDER in result
        assert "user@example.com" not in result

    def test_ip(self):
        result = redact("server at 10.0.0.1 responded")
        assert "10.0.0.1" not in result

    def test_no_match(self):
        text = "nothing to redact here"
        assert redact(text) == text

    def test_custom_pattern(self):
        extra = [re.compile(r"SECRET\d+")]
        result = redact("my SECRET12345 value", extra)
        assert "SECRET12345" not in result


class TestRedactRecord:
    def test_redacts_raw_and_views(self):
        meta = IngestMetadata(source_file="test.txt", source_format="text")
        record = build_record("test user@example.com data", meta)
        redacted = redact_record(record)
        assert record.redacted_raw is not None
        assert "user@example.com" not in record.redacted_raw

    def test_fingerprints_unchanged(self):
        meta = IngestMetadata(source_file="test.txt", source_format="text")
        record = build_record("test user@example.com data", meta)
        original_fp = record.fingerprints.raw_sha256
        redact_record(record)
        assert record.fingerprints.raw_sha256 == original_fp
