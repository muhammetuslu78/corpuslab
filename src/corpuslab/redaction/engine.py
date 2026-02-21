"""Redaction pipeline."""

from __future__ import annotations

import re
from typing import List, Optional

from corpuslab.constants import REDACTION_PLACEHOLDER
from corpuslab.models import PayloadRecord
from corpuslab.redaction.patterns import BUILTIN_PATTERNS


def redact(text: str, extra_patterns: Optional[List[re.Pattern]] = None) -> str:
    """Apply all redaction patterns to text."""
    result = text
    all_patterns = list(BUILTIN_PATTERNS.values()) + (extra_patterns or [])
    for pattern in all_patterns:
        result = pattern.sub(REDACTION_PLACEHOLDER, result)
    return result


def redact_record(
    record: PayloadRecord,
    extra_patterns: Optional[List[re.Pattern]] = None,
) -> PayloadRecord:
    """Redact a record's raw payload and canonical views.

    Fingerprints remain unchanged (computed from pre-redaction data).
    """
    record.redacted_raw = redact(record.raw, extra_patterns)
    for view in record.canonical_views:
        view.value = redact(view.value, extra_patterns)
    return record
