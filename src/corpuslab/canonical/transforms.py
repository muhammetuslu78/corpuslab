"""Pure transform functions for canonical views."""

from __future__ import annotations

import html
import unicodedata
from urllib.parse import unquote

from corpuslab.constants import MAX_URL_DECODE_DEPTH


def url_decode_single(s: str) -> str:
    """Single-pass URL decode."""
    return unquote(s)


def url_decode_deep(s: str, max_depth: int = MAX_URL_DECODE_DEPTH) -> str:
    """Iterative URL decode until stable or max depth reached."""
    current = s
    for _ in range(max_depth):
        decoded = unquote(current)
        if decoded == current:
            break
        current = decoded
    return current


def html_unescape(s: str) -> str:
    """Decode HTML entities."""
    return html.unescape(s)


def nfkc_normalize(s: str) -> str:
    """Unicode NFKC normalization."""
    return unicodedata.normalize("NFKC", s)
