"""JSONL corpus file read/write operations."""

from __future__ import annotations

import os
from typing import Iterator, Set

from corpuslab.models import PayloadRecord


def iterate_corpus(path: str) -> Iterator[PayloadRecord]:
    """Streaming reader: yields one PayloadRecord per line."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                yield PayloadRecord.model_validate_json(stripped)


def write_corpus(path: str, records: Iterator[PayloadRecord]) -> int:
    """Write records to a JSONL corpus file. Returns count written."""
    count = 0
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")
            count += 1
    return count


def append_record(path: str, record: PayloadRecord) -> None:
    """Append a single record to an existing corpus file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")


def dedup_merge(
    existing_path: str, new_records: Iterator[PayloadRecord]
) -> Iterator[PayloadRecord]:
    """Merge new records into existing corpus, skipping duplicates by id."""
    seen: Set[str] = set()
    if os.path.exists(existing_path):
        for record in iterate_corpus(existing_path):
            seen.add(record.id)
            yield record
    for record in new_records:
        if record.id not in seen:
            seen.add(record.id)
            yield record


def corpus_ids(path: str) -> Set[str]:
    """Return set of all record IDs in a corpus file."""
    ids: Set[str] = set()
    if not os.path.exists(path):
        return ids
    for record in iterate_corpus(path):
        ids.add(record.id)
    return ids
