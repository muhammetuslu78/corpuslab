"""Canonical view computation engine."""

from __future__ import annotations

from typing import List

from corpuslab.canonical.trace import traced_transform
from corpuslab.canonical.transforms import (
    html_unescape,
    nfkc_normalize,
    url_decode_deep,
    url_decode_single,
)
from corpuslab.models import CanonicalView


def compute_canonical_views(raw: str) -> List[CanonicalView]:
    """Compute all canonical analysis views for a raw payload."""
    views: List[CanonicalView] = []

    # View 1: Single URL-decode
    val, step = traced_transform("url_decode_single", url_decode_single, raw)
    views.append(CanonicalView(name="url_decoded", value=val, trace=[step]))

    # View 2: Deep URL-decode
    val, step = traced_transform("url_decode_deep", url_decode_deep, raw)
    views.append(CanonicalView(name="url_decoded_deep", value=val, trace=[step]))

    # View 3: HTML entity decode
    val, step = traced_transform("html_unescape", html_unescape, raw)
    views.append(CanonicalView(name="html_decoded", value=val, trace=[step]))

    # View 4: Full NFKC normalized (URL-decode → HTML-unescape → NFKC)
    trace = []
    current = raw
    for name, fn in [
        ("url_decode_deep", url_decode_deep),
        ("html_unescape", html_unescape),
        ("nfkc_normalize", nfkc_normalize),
    ]:
        current, step = traced_transform(name, fn, current)
        trace.append(step)
    views.append(CanonicalView(name="nfkc_normalized", value=current, trace=trace))

    return views
