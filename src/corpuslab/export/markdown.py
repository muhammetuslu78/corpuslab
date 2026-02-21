"""Markdown report generation."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterator, List, Optional, Tuple

from corpuslab import __version__
from corpuslab.constants import MAX_DISPLAY_LENGTH
from corpuslab.models import PayloadRecord


def export_markdown(
    records: Iterator[PayloadRecord],
    output_path: str,
    config_hash: Optional[str] = None,
    top_n: int = 10,
    use_redacted: bool = False,
) -> int:
    """Generate a Markdown analysis report. Returns record count."""
    # Materialize for multi-pass analysis
    all_records: List[PayloadRecord] = sorted(
        list(records), key=lambda r: r.id
    )
    if not all_records:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# CorpusLab Report\n\nNo records to report.\n")
        return 0

    # Compute stats
    tag_counter: Counter = Counter()
    tag_combo_counter: Counter = Counter()
    cluster_sizes: Counter = Counter()
    source_counter: Counter = Counter()
    length_sum = 0
    anomalies_long: List[PayloadRecord] = []
    anomalies_entropy: List[PayloadRecord] = []
    anomalies_depth: List[PayloadRecord] = []

    for rec in all_records:
        tag_names = sorted(t.tag.value for t in rec.tags)
        for tn in tag_names:
            tag_counter[tn] += 1
        if tag_names:
            tag_combo_counter[tuple(tag_names)] += 1
        if rec.cluster_id:
            cluster_sizes[rec.cluster_id] += 1
        if rec.ingest_meta.source_file:
            source_counter[rec.ingest_meta.source_file] += 1
        length_sum += rec.raw_length

        # Anomalies
        for t in rec.tags:
            if t.tag.value == "very_long_input":
                anomalies_long.append(rec)
            if t.tag.value == "high_entropy":
                anomalies_entropy.append(rec)

    avg_length = length_sum / len(all_records) if all_records else 0
    now = datetime.now(timezone.utc).isoformat()

    lines: List[str] = []
    lines.append("# CorpusLab Analysis Report\n")

    # Run manifest
    lines.append("## Run Manifest\n")
    lines.append(f"- **Tool version:** {__version__}")
    lines.append(f"- **Generated at:** {now}")
    lines.append(f"- **Config hash:** {config_hash or 'default'}")
    lines.append(f"- **Record count:** {len(all_records)}")
    lines.append("")

    # Ingest summary
    lines.append("## Ingest Summary\n")
    lines.append(f"- **Total records:** {len(all_records)}")
    lines.append(f"- **Average payload length:** {avg_length:.0f}")
    lines.append(f"- **Sources:** {len(source_counter)}")
    if source_counter:
        lines.append("")
        lines.append("| Source | Count |")
        lines.append("|--------|-------|")
        for src, cnt in source_counter.most_common(top_n):
            lines.append(f"| {src} | {cnt} |")
    lines.append("")

    # Tag distribution
    lines.append("## Tag Distribution\n")
    lines.append("| Tag | Count | Percentage |")
    lines.append("|-----|-------|------------|")
    for tag, cnt in tag_counter.most_common():
        pct = cnt / len(all_records) * 100
        lines.append(f"| {tag} | {cnt} | {pct:.1f}% |")
    lines.append("")

    # Top tag combinations
    lines.append("## Top Tag Combinations\n")
    lines.append("| Combination | Count |")
    lines.append("|-------------|-------|")
    for combo, cnt in tag_combo_counter.most_common(top_n):
        combo_str = " + ".join(combo)
        lines.append(f"| {combo_str} | {cnt} |")
    lines.append("")

    # Cluster summary
    if cluster_sizes:
        lines.append("## Cluster Summary\n")
        unique_clusters = len(cluster_sizes)
        lines.append(f"- **Total clusters:** {unique_clusters}")
        lines.append(f"- **Largest cluster size:** {cluster_sizes.most_common(1)[0][1]}")
        lines.append("")
        lines.append("| Cluster ID | Size |")
        lines.append("|------------|------|")
        for cid, size in cluster_sizes.most_common(top_n):
            lines.append(f"| {cid[:16]}... | {size} |")
        lines.append("")

    # Anomalies
    lines.append("## Anomalies\n")

    if anomalies_long:
        lines.append(f"### Very Long Inputs ({len(anomalies_long)})\n")
        for rec in anomalies_long[:5]:
            display = rec.redacted_raw if (use_redacted and rec.redacted_raw) else rec.raw
            lines.append(f"- `{display[:MAX_DISPLAY_LENGTH]}...` (length={rec.raw_length})")
        lines.append("")

    if anomalies_entropy:
        lines.append(f"### High Entropy ({len(anomalies_entropy)})\n")
        for rec in anomalies_entropy[:5]:
            display = rec.redacted_raw if (use_redacted and rec.redacted_raw) else rec.raw
            ent_tag = next((t for t in rec.tags if t.tag.value == "high_entropy"), None)
            ent_val = ent_tag.features.get("entropy", "?") if ent_tag else "?"
            lines.append(f"- `{display[:MAX_DISPLAY_LENGTH]}...` (entropy={ent_val})")
        lines.append("")

    if not anomalies_long and not anomalies_entropy:
        lines.append("No anomalies detected.\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return len(all_records)
