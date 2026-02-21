"""Tests for fingerprint hasher."""

from corpuslab.canonical.engine import compute_canonical_views
from corpuslab.fingerprint.hasher import (
    compute_fingerprints,
    length_bucket,
    sha256_hex,
)
from corpuslab.tagging.registry import run_all_detectors


class TestSha256:
    def test_deterministic(self):
        assert sha256_hex("hello") == sha256_hex("hello")

    def test_different_inputs(self):
        assert sha256_hex("hello") != sha256_hex("world")

    def test_hex_format(self):
        h = sha256_hex("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestLengthBucket:
    def test_small(self):
        assert length_bucket(10) == "0-64"

    def test_medium(self):
        assert length_bucket(100) == "65-256"

    def test_large(self):
        assert length_bucket(500) == "257-1024"

    def test_very_large(self):
        assert length_bucket(2000) == "1025+"


class TestComputeFingerprints:
    def test_produces_all_fields(self):
        raw = "test payload"
        views = compute_canonical_views(raw)
        tags = run_all_detectors(raw)
        fp = compute_fingerprints(raw, views, tags)

        assert fp.raw_sha256
        assert fp.canonical_sha256_nfkc
        assert fp.canonical_sha256_url_decoded
        assert fp.canonical_sha256_html_decoded
        assert fp.length_bucket
        assert fp.structure_hash

    def test_deterministic(self):
        raw = "test payload"
        views = compute_canonical_views(raw)
        tags = run_all_detectors(raw)
        fp1 = compute_fingerprints(raw, views, tags)
        fp2 = compute_fingerprints(raw, views, tags)
        assert fp1 == fp2
