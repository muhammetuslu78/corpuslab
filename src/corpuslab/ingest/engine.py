"""Ingestion orchestrator: reader -> tag -> canonicalize -> fingerprint -> yield."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterator, List, Optional

from corpuslab.canonical.engine import compute_canonical_views
from corpuslab.fingerprint.hasher import compute_fingerprints, sha256_hex
from corpuslab.ingest.detect import detect_format
from corpuslab.ingest.readers import read_csv, read_json_array, read_jsonl, read_text_lines
from corpuslab.models import IngestMetadata, PayloadRecord
from corpuslab.redaction.engine import redact_record
from corpuslab.redaction.custom import compile_user_patterns
from corpuslab.tagging.registry import run_all_detectors

_READERS = {
    "text": read_text_lines,
    "csv": read_csv,
    "json": read_json_array,
    "jsonl": read_jsonl,
    "ndjson": read_jsonl,
}


def build_record(raw: str, meta: IngestMetadata) -> PayloadRecord:
    """Build a complete PayloadRecord from raw payload and metadata."""
    tags = run_all_detectors(raw)
    canonical_views = compute_canonical_views(raw)
    fingerprints = compute_fingerprints(raw, canonical_views, tags)

    return PayloadRecord(
        id=fingerprints.raw_sha256,
        raw=raw,
        raw_length=len(raw),
        tags=tags,
        canonical_views=canonical_views,
        fingerprints=fingerprints,
        ingest_meta=meta,
    )


def ingest_stream(
    source: str,
    fmt: str = "auto",
    field: Optional[str] = None,
    redact: bool = False,
    redact_patterns: Optional[List[str]] = None,
    environment: Optional[str] = None,
    collection_method: Optional[str] = None,
) -> Iterator[PayloadRecord]:
    """Stream payloads from a source file, producing PayloadRecords."""
    if fmt == "auto":
        fmt = detect_format(source)

    reader_fn = _READERS.get(fmt)
    if reader_fn is None:
        raise ValueError(f"Unsupported format: {fmt}")

    # Prepare reader args
    if fmt in ("csv", "json", "jsonl", "ndjson"):
        reader = reader_fn(source, field)
    else:
        reader = reader_fn(source)

    extra_patterns = compile_user_patterns(redact_patterns or []) if redact_patterns else []
    now = datetime.now(timezone.utc).isoformat()

    for raw_payload, meta_partial in reader:
        meta = IngestMetadata(
            source_file=source,
            source_format=fmt,
            environment=environment,
            collection_method=collection_method,
            ingested_at=now,
            **meta_partial,
        )
        record = build_record(raw_payload, meta)
        if redact:
            record = redact_record(record, extra_patterns)
        yield record
