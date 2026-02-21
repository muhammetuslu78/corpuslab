"""Format auto-detection for input files."""

from __future__ import annotations

import json
import os


def detect_format(path: str) -> str:
    """Detect input file format by extension and content heuristics."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return "csv"
    if ext == ".json":
        return "json"
    if ext in (".jsonl", ".ndjson"):
        return "jsonl"
    if ext == ".txt":
        return "text"

    # Heuristic: read first 4KB
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            head = f.read(4096)
    except OSError:
        return "text"

    stripped = head.lstrip()
    if not stripped:
        return "text"

    # JSON array or object
    if stripped.startswith("[") or stripped.startswith("{"):
        # Check if first line is a complete JSON object (JSONL)
        first_line = stripped.split("\n", 1)[0].strip()
        if first_line.startswith("{"):
            try:
                json.loads(first_line)
                return "jsonl"
            except json.JSONDecodeError:
                pass
        return "json"

    # CSV heuristic: first line contains commas and looks like a header
    first_line = stripped.split("\n", 1)[0]
    if "," in first_line and not first_line.startswith("<"):
        commas = first_line.count(",")
        if commas >= 1:
            return "csv"

    return "text"
