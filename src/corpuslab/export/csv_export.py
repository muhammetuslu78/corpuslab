"""CSV export with field flattening."""

from __future__ import annotations

import csv
from typing import Dict, Iterator, List, Optional

from corpuslab.models import PayloadRecord

DEFAULT_FIELDS = [
    "id",
    "raw_length",
    "tags",
    "cluster_id",
    "source_file",
    "source_format",
    "raw_sha256",
    "length_bucket",
]


def flatten_record(record: PayloadRecord, use_redacted: bool = False) -> Dict[str, str]:
    """Flatten a PayloadRecord to a dict of string values for CSV."""
    raw_display = record.redacted_raw if (use_redacted and record.redacted_raw) else record.raw
    flat: Dict[str, str] = {
        "id": record.id,
        "raw": raw_display,
        "raw_length": str(record.raw_length),
        "tags": ",".join(t.tag.value for t in record.tags),
        "tag_count": str(len(record.tags)),
        "cluster_id": record.cluster_id or "",
        "source_file": record.ingest_meta.source_file or "",
        "source_format": record.ingest_meta.source_format,
        "line_number": str(record.ingest_meta.line_number or ""),
        "environment": record.ingest_meta.environment or "",
        "collection_method": record.ingest_meta.collection_method or "",
        "ingested_at": record.ingest_meta.ingested_at or "",
    }
    if record.fingerprints:
        flat["raw_sha256"] = record.fingerprints.raw_sha256
        flat["canonical_sha256_nfkc"] = record.fingerprints.canonical_sha256_nfkc
        flat["length_bucket"] = record.fingerprints.length_bucket
        flat["structure_hash"] = record.fingerprints.structure_hash
    return flat


def export_csv(
    records: Iterator[PayloadRecord],
    output_path: str,
    fields: Optional[List[str]] = None,
    use_redacted: bool = False,
) -> int:
    """Export records to CSV. Returns count written."""
    all_rows = []
    for record in records:
        all_rows.append(flatten_record(record, use_redacted))

    if not all_rows:
        return 0

    fieldnames = fields if fields else DEFAULT_FIELDS
    # Ensure all requested fields exist
    available = set(all_rows[0].keys())
    fieldnames = [f for f in fieldnames if f in available]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    return len(all_rows)
