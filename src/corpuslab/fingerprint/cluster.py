"""Clustering by fingerprint similarity."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterator, List, Optional, Tuple

from corpuslab.models import PayloadRecord


def cluster_by_fingerprint(
    records: Iterator[PayloadRecord],
    key: str = "canonical_sha256_nfkc",
) -> Dict[str, List[str]]:
    """Group records by a chosen fingerprint field. Returns {fingerprint: [record_ids]}."""
    clusters: Dict[str, List[str]] = defaultdict(list)
    for record in records:
        if record.fingerprints is None:
            continue
        fp_value = getattr(record.fingerprints, key, None)
        if fp_value:
            clusters[fp_value].append(record.id)
    return dict(clusters)


def assign_cluster_ids(
    records: Iterator[PayloadRecord],
    key: str = "canonical_sha256_nfkc",
) -> Iterator[PayloadRecord]:
    """Two-pass: first build clusters, then yield records with cluster_id assigned.

    Note: This materializes all records in memory for the first pass.
    """
    all_records: List[PayloadRecord] = list(records)

    # Build cluster map
    clusters: Dict[str, List[str]] = defaultdict(list)
    for record in all_records:
        if record.fingerprints is None:
            continue
        fp_value = getattr(record.fingerprints, key, None)
        if fp_value:
            clusters[fp_value].append(record.id)

    # Build reverse map: record_id -> cluster_id (fingerprint value)
    id_to_cluster: Dict[str, str] = {}
    for fp, record_ids in clusters.items():
        for rid in record_ids:
            id_to_cluster[rid] = fp

    # Yield records with cluster_id
    for record in all_records:
        record.cluster_id = id_to_cluster.get(record.id)
        yield record


def cluster_stats(
    records: Iterator[PayloadRecord],
) -> List[Dict]:
    """Compute cluster statistics from records that have cluster_id assigned."""
    cluster_data: Dict[str, Dict] = defaultdict(lambda: {
        "size": 0,
        "sources": set(),
        "tags": defaultdict(int),
    })
    for record in records:
        cid = record.cluster_id
        if cid is None:
            continue
        data = cluster_data[cid]
        data["size"] += 1
        if record.ingest_meta.source_file:
            data["sources"].add(record.ingest_meta.source_file)
        for tag in record.tags:
            data["tags"][tag.tag.value] += 1

    stats = []
    for cid, data in sorted(cluster_data.items(), key=lambda x: x[1]["size"], reverse=True):
        stats.append({
            "cluster_id": cid[:16] + "...",
            "size": data["size"],
            "sources": sorted(data["sources"]),
            "tag_distribution": dict(data["tags"]),
        })
    return stats
