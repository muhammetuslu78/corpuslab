"""Shared test fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from corpuslab.models import IngestMetadata, PayloadRecord
from corpuslab.ingest.engine import build_record

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR


@pytest.fixture
def sample_text_path():
    return str(FIXTURES_DIR / "sample_payloads.txt")


@pytest.fixture
def sample_csv_path():
    return str(FIXTURES_DIR / "sample_payloads.csv")


@pytest.fixture
def sample_json_path():
    return str(FIXTURES_DIR / "sample_payloads.json")


@pytest.fixture
def sample_jsonl_path():
    return str(FIXTURES_DIR / "sample_payloads.jsonl")


@pytest.fixture
def url_encoded_payload():
    return "%3Cscript%3Ealert%28document.cookie%29%3C%2Fscript%3E"


@pytest.fixture
def base64_payload():
    return "dGhpcyBpcyBhIHRlc3QgcGF5bG9hZCBmb3IgYmFzZTY0IGRldGVjdGlvbg=="


@pytest.fixture
def html_entity_payload():
    return "&lt;script&gt;alert(1)&lt;/script&gt;"


@pytest.fixture
def cleartext_payload():
    return "hello world simple test"


@pytest.fixture
def mixed_payload():
    return "%3Cimg%20src%3Dx%20onerror%3D&#x61;&#x6c;&#x65;&#x72;&#x74;(1)%3E"


@pytest.fixture
def sample_record(cleartext_payload):
    meta = IngestMetadata(source_file="test.txt", source_format="text", line_number=1)
    return build_record(cleartext_payload, meta)


@pytest.fixture
def tmp_corpus(tmp_path, sample_text_path):
    """Create a small corpus from sample_payloads.txt."""
    from corpuslab.ingest.engine import ingest_stream
    from corpuslab.storage.corpus import write_corpus

    corpus_path = str(tmp_path / "test_corpus.jsonl")
    records = ingest_stream(sample_text_path, "text")
    write_corpus(corpus_path, records)
    return corpus_path
