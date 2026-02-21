"""JSONL export."""

from __future__ import annotations

from typing import Iterator

from corpuslab.models import PayloadRecord


def export_jsonl(records: Iterator[PayloadRecord], output_path: str) -> int:
    """Write records to JSONL file. Returns count written."""
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
            count += 1
    return count
