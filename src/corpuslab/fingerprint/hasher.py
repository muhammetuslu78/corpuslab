"""Deterministic fingerprint computation."""

from __future__ import annotations

import hashlib
from typing import List

from corpuslab.constants import LENGTH_BUCKET_OVERFLOW, LENGTH_BUCKETS
from corpuslab.models import CanonicalView, Fingerprints, TagResult


def sha256_hex(s: str) -> str:
    """Compute SHA-256 hex digest of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def length_bucket(n: int) -> str:
    """Assign a length to a bucket string."""
    for threshold, label in LENGTH_BUCKETS:
        if n <= threshold:
            return label
    return LENGTH_BUCKET_OVERFLOW


def compute_fingerprints(
    raw: str,
    canonical_views: List[CanonicalView],
    tags: List[TagResult],
) -> Fingerprints:
    """Compute all fingerprints for a payload."""
    cv = {v.name: v.value for v in canonical_views}
    tag_set = sorted(t.tag.value for t in tags if t.confidence >= 0.5)

    return Fingerprints(
        raw_sha256=sha256_hex(raw),
        canonical_sha256_nfkc=sha256_hex(cv.get("nfkc_normalized", raw)),
        canonical_sha256_url_decoded=sha256_hex(cv.get("url_decoded", raw)),
        canonical_sha256_html_decoded=sha256_hex(cv.get("html_decoded", raw)),
        length_bucket=length_bucket(len(raw)),
        structure_hash=sha256_hex("|".join(tag_set)),
    )
