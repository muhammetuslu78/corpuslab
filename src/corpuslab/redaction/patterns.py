"""Built-in redaction patterns for PII and secrets."""

from __future__ import annotations

import re

from corpuslab.constants import REDACTION_PLACEHOLDER

BUILTIN_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "jwt": re.compile(
        r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
    ),
    "bearer_token": re.compile(r"(?i)(?:bearer\s+)[A-Za-z0-9_\-.]{20,}"),
    "api_key_assignment": re.compile(
        r"(?i)(?:api[_-]?key|token|secret|password)[=:]\s*[A-Za-z0-9_\-.]{16,}"
    ),
    "ipv4": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}
