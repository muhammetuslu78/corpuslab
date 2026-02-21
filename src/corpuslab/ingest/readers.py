"""Format-specific streaming readers."""

from __future__ import annotations

import csv
import json
from typing import Dict, Iterator, Optional, Tuple


def read_text_lines(path: str) -> Iterator[Tuple[str, Dict]]:
    """Yields one payload per non-empty line."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            stripped = line.rstrip("\n\r")
            if stripped:
                yield stripped, {"line_number": line_no}


def read_csv(path: str, field: Optional[str] = None) -> Iterator[Tuple[str, Dict]]:
    """Stream CSV rows, extracting payload from specified field or first column."""
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return
        target_field = field if field and field in reader.fieldnames else reader.fieldnames[0]
        for line_no, row in enumerate(reader, 2):  # line 1 is header
            value = row.get(target_field, "")
            if value and value.strip():
                yield value.strip(), {"line_number": line_no, "field_name": target_field}


def read_json_array(path: str, field: Optional[str] = None) -> Iterator[Tuple[str, Dict]]:
    """Read a JSON file. Handles arrays of strings or arrays of objects."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        data = json.load(f)

    if isinstance(data, list):
        for idx, item in enumerate(data):
            payload = _extract_payload(item, field)
            if payload:
                yield payload, {"line_number": idx + 1, "field_name": field}
    elif isinstance(data, dict):
        payload = _extract_payload(data, field)
        if payload:
            yield payload, {"line_number": 1, "field_name": field}


def read_jsonl(path: str, field: Optional[str] = None) -> Iterator[Tuple[str, Dict]]:
    """JSONL/NDJSON: one JSON object per line."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            payload = _extract_payload(obj, field)
            if payload:
                yield payload, {"line_number": line_no, "field_name": field}


def _extract_payload(item: object, field: Optional[str] = None) -> Optional[str]:
    """Extract a payload string from a JSON item."""
    if isinstance(item, str):
        return item.strip() if item.strip() else None
    if isinstance(item, dict):
        if field and field in item:
            val = item[field]
            return str(val).strip() if val else None
        # Try common field names
        for key in ("payload", "raw", "value", "data", "input", "string"):
            if key in item:
                val = item[key]
                return str(val).strip() if val else None
        # Fall back to first string value
        for val in item.values():
            if isinstance(val, str) and val.strip():
                return val.strip()
    return None
