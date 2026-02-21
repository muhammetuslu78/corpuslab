"""Tests for clustering."""

from corpuslab.fingerprint.cluster import assign_cluster_ids, cluster_by_fingerprint, cluster_stats
from corpuslab.ingest.engine import build_record
from corpuslab.models import IngestMetadata


def _build(raw: str) -> "PayloadRecord":
    meta = IngestMetadata(source_file="test.txt", source_format="text")
    return build_record(raw, meta)


class TestClusterByFingerprint:
    def test_groups_identical(self):
        records = [_build("hello"), _build("hello")]
        clusters = cluster_by_fingerprint(iter(records))
        # Identical records have same fingerprint, but same id so list has 2
        for key, ids in clusters.items():
            assert len(ids) == 2

    def test_separates_different(self):
        records = [_build("hello"), _build("world")]
        clusters = cluster_by_fingerprint(iter(records))
        assert len(clusters) == 2


class TestAssignClusterIds:
    def test_assigns_ids(self):
        records = [_build("hello"), _build("world")]
        clustered = list(assign_cluster_ids(iter(records)))
        assert all(r.cluster_id is not None for r in clustered)

    def test_same_payload_same_cluster(self):
        records = [_build("hello"), _build("hello")]
        clustered = list(assign_cluster_ids(iter(records)))
        assert clustered[0].cluster_id == clustered[1].cluster_id
