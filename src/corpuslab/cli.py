"""CorpusLab CLI - security payload corpus management."""

from __future__ import annotations

import json
import os
import random
import string
import sys
from base64 import b64encode
from collections import Counter
from typing import List, Optional
from urllib.parse import quote

import click

from corpuslab import __version__
from corpuslab.constants import MAX_DISPLAY_LENGTH


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """CorpusLab - Security payload corpus management."""


@cli.command("import")
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "--format", "fmt",
    type=click.Choice(["auto", "text", "csv", "json", "jsonl", "ndjson"]),
    default="auto",
    help="Input format (default: auto-detect)",
)
@click.option("--field", help="Field name containing payload (CSV/JSON)")
@click.option("--output", "-o", type=click.Path(), default="corpus.jsonl", help="Output corpus file")
@click.option("--redact/--no-redact", default=False, help="Enable PII/secret redaction")
@click.option("--redact-pattern", multiple=True, help="Additional regex patterns to redact")
@click.option("--append/--overwrite", default=True, help="Append to or overwrite output")
@click.option("--environment", help="Environment tag (prod/stage/dev)")
@click.option("--collection-method", help="Collection method (log/test/manual)")
def import_cmd(
    source: str,
    fmt: str,
    field: Optional[str],
    output: str,
    redact: bool,
    redact_pattern: tuple,
    append: bool,
    environment: Optional[str],
    collection_method: Optional[str],
) -> None:
    """Ingest payloads from a file into the corpus."""
    from corpuslab.ingest.engine import ingest_stream
    from corpuslab.storage.corpus import corpus_ids, write_corpus

    seen = set()
    if append and os.path.exists(output):
        seen = corpus_ids(output)
        click.echo(f"Existing corpus: {len(seen)} records")

    count = 0
    mode = "a" if (append and os.path.exists(output)) else "w"
    with open(output, mode, encoding="utf-8") as f:
        for record in ingest_stream(
            source, fmt, field, redact, list(redact_pattern),
            environment, collection_method,
        ):
            if record.id not in seen:
                f.write(record.model_dump_json() + "\n")
                seen.add(record.id)
                count += 1

    click.echo(f"Imported {count} records to {output}")


@cli.command()
@click.argument("corpus", type=click.Path(exists=True))
@click.option("--top", type=int, default=10, help="Number of top items to show")
def summarize(corpus: str, top: int) -> None:
    """Show corpus statistics and tag distribution."""
    from corpuslab.storage.corpus import iterate_corpus

    tag_counter: Counter = Counter()
    tag_combo_counter: Counter = Counter()
    cluster_sizes: Counter = Counter()
    total = 0
    length_sum = 0

    for record in iterate_corpus(corpus):
        total += 1
        length_sum += record.raw_length
        tag_names = sorted(t.tag.value for t in record.tags)
        for tn in tag_names:
            tag_counter[tn] += 1
        if tag_names:
            tag_combo_counter[tuple(tag_names)] += 1
        if record.cluster_id:
            cluster_sizes[record.cluster_id] += 1

    click.echo(f"Total records: {total}")
    click.echo(f"Average length: {length_sum / total:.0f}" if total else "Average length: 0")
    click.echo()

    click.echo("Tag distribution:")
    for tag, cnt in tag_counter.most_common(top):
        pct = cnt / total * 100 if total else 0
        click.echo(f"  {tag}: {cnt} ({pct:.1f}%)")
    click.echo()

    click.echo("Top tag combinations:")
    for combo, cnt in tag_combo_counter.most_common(top):
        click.echo(f"  {' + '.join(combo)}: {cnt}")

    if cluster_sizes:
        click.echo()
        click.echo(f"Clusters: {len(cluster_sizes)}")
        click.echo("Top clusters by size:")
        for cid, size in cluster_sizes.most_common(top):
            click.echo(f"  {cid[:16]}...: {size}")


@cli.command("filter")
@click.argument("corpus", type=click.Path(exists=True))
@click.option("--tag", multiple=True, help="Include records with this tag")
@click.option("--exclude-tag", multiple=True, help="Exclude records with this tag")
@click.option("--min-confidence", type=float, default=0.0, help="Min confidence threshold")
@click.option("--min-length", type=int, help="Minimum payload length")
@click.option("--max-length", type=int, help="Maximum payload length")
@click.option("--source", "source_filter", help="Filter by source file name")
@click.option("--has-non-ascii/--no-non-ascii", default=None, help="Filter by non-ASCII presence")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout as summary)")
def filter_cmd(
    corpus: str,
    tag: tuple,
    exclude_tag: tuple,
    min_confidence: float,
    min_length: Optional[int],
    max_length: Optional[int],
    source_filter: Optional[str],
    has_non_ascii: Optional[bool],
    output: Optional[str],
) -> None:
    """Filter corpus by tags, confidence, length, and other criteria."""
    from corpuslab.storage.corpus import iterate_corpus

    count = 0
    matched = 0
    out_f = open(output, "w", encoding="utf-8") if output else None

    try:
        for record in iterate_corpus(corpus):
            count += 1
            # Apply filters
            record_tags = {
                t.tag.value: t.confidence for t in record.tags
            }

            if tag:
                if not any(
                    t in record_tags and record_tags[t] >= min_confidence
                    for t in tag
                ):
                    continue

            if exclude_tag:
                if any(t in record_tags for t in exclude_tag):
                    continue

            if min_length and record.raw_length < min_length:
                continue
            if max_length and record.raw_length > max_length:
                continue

            if source_filter and record.ingest_meta.source_file:
                if source_filter not in record.ingest_meta.source_file:
                    continue

            matched += 1
            if out_f:
                out_f.write(record.model_dump_json() + "\n")
            else:
                tags_str = ", ".join(
                    f"{t.tag.value}({t.confidence:.2f})" for t in record.tags
                )
                display = record.raw[:MAX_DISPLAY_LENGTH]
                click.echo(f"[{record.id[:12]}] len={record.raw_length} tags=[{tags_str}]")
    finally:
        if out_f:
            out_f.close()

    click.echo(f"\nMatched {matched}/{count} records")
    if output:
        click.echo(f"Written to {output}")


@cli.command()
@click.argument("corpus", type=click.Path(exists=True))
@click.option(
    "--by",
    type=click.Choice([
        "canonical_sha256_nfkc",
        "canonical_sha256_url_decoded",
        "canonical_sha256_html_decoded",
        "structure_hash",
    ]),
    default="canonical_sha256_nfkc",
    help="Fingerprint field to cluster by",
)
@click.option("--output", "-o", type=click.Path(), help="Output corpus file with cluster IDs")
def cluster(corpus: str, by: str, output: Optional[str]) -> None:
    """Cluster payloads by fingerprint similarity."""
    from corpuslab.fingerprint.cluster import assign_cluster_ids, cluster_stats
    from corpuslab.storage.corpus import iterate_corpus, write_corpus

    out_path = output or corpus
    records = list(assign_cluster_ids(iterate_corpus(corpus), key=by))
    write_corpus(out_path, iter(records))

    stats = cluster_stats(iter(records))
    click.echo(f"Clustered {len(records)} records into {len(stats)} clusters (by {by})")
    click.echo("\nTop clusters:")
    for s in stats[:10]:
        click.echo(f"  {s['cluster_id']}: size={s['size']}")
    if output:
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.argument("corpus", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="report.md", help="Output report file")
@click.option("--top", type=int, default=10, help="Number of top items in report")
@click.option("--redacted/--no-redacted", default=False, help="Use redacted payloads in report")
def report(corpus: str, output: str, top: int, redacted: bool) -> None:
    """Generate a Markdown analysis report."""
    from corpuslab.export.markdown import export_markdown
    from corpuslab.storage.corpus import iterate_corpus

    count = export_markdown(iterate_corpus(corpus), output, top_n=top, use_redacted=redacted)
    click.echo(f"Report generated: {output} ({count} records)")


@cli.command()
@click.argument("corpus", type=click.Path(exists=True))
@click.option(
    "--format", "fmt",
    type=click.Choice(["jsonl", "csv", "markdown"]),
    default="jsonl",
    help="Export format",
)
@click.option("--output", "-o", type=click.Path(), required=True, help="Output file path")
@click.option("--fields", help="Comma-separated field list for CSV")
@click.option("--redacted/--no-redacted", default=False, help="Use redacted content")
def export(corpus: str, fmt: str, output: str, fields: Optional[str], redacted: bool) -> None:
    """Export corpus to JSONL, CSV, or Markdown."""
    from corpuslab.export.csv_export import export_csv
    from corpuslab.export.jsonl import export_jsonl
    from corpuslab.export.markdown import export_markdown
    from corpuslab.storage.corpus import iterate_corpus

    field_list = [f.strip() for f in fields.split(",")] if fields else None

    if fmt == "jsonl":
        count = export_jsonl(iterate_corpus(corpus), output)
    elif fmt == "csv":
        count = export_csv(iterate_corpus(corpus), output, field_list, use_redacted=redacted)
    elif fmt == "markdown":
        count = export_markdown(iterate_corpus(corpus), output, use_redacted=redacted)
    else:
        click.echo(f"Unknown format: {fmt}", err=True)
        sys.exit(1)

    click.echo(f"Exported {count} records to {output} ({fmt})")


@cli.command()
@click.option("--count", "-n", type=int, default=100, help="Number of payloads to generate")
@click.option("--output", "-o", type=click.Path(), default="synthetic_payloads.txt", help="Output file")
@click.option("--seed", type=int, default=42, help="Random seed for reproducibility")
def generate(count: int, output: str, seed: int) -> None:
    """Generate synthetic (non-malicious) test payloads covering all tag types."""
    rng = random.Random(seed)
    payloads: List[str] = []

    # Cleartext samples
    cleartext_samples = [
        "hello world",
        "simple test string",
        "the quick brown fox jumps over the lazy dog",
        "username=testuser&action=login&page=home",
        "GET /api/v1/users HTTP/1.1",
    ]

    # URL-encoded samples
    url_encoded_samples = [
        quote("hello world <test>"),
        quote("param=value&other=<data>"),
        quote("path/to/resource?q=search term"),
    ]

    # Multi-URL-encoded
    multi_url = quote(quote(quote("nested <encoding> test")))

    # HTML entities
    html_samples = [
        "&lt;div&gt;test content&lt;/div&gt;",
        "value &amp; another &#60;value&#62;",
        "&#x3C;span&#x3E;html hex entities&#x3C;/span&#x3E;",
    ]

    # Unicode escapes
    unicode_samples = [
        "\\u0048\\u0065\\u006C\\u006C\\u006F",
        "test\\x41\\x42\\x43data",
        "\\u003Ctest\\u003E\\u0026\\u003C/test\\u003E",
    ]

    # JSON escaped
    json_samples = [
        '{"key": "value with \\"quotes\\" and \\n newlines"}',
        'path\\\\to\\\\file\\/resource',
        'tab\\there\\nand\\nnewlines',
    ]

    # Base64-like
    b64_samples = [
        b64encode(b"this is a test payload for base64 detection").decode(),
        b64encode(b"another sample string with enough length").decode(),
    ]

    # Whitespace obfuscation
    ws_samples = [
        "test\tcontent\twith\ttabs",
        "multiple   spaces   between   words",
        "mixed\t  whitespace\t  patterns",
    ]

    # Non-ASCII
    non_ascii_samples = [
        "caf\u00e9 na\u00efve r\u00e9sum\u00e9",
        "\u4f60\u597d\u4e16\u754c test",
        "data \u2192 result \u2190 input",
    ]

    # High entropy (random-looking)
    high_entropy_samples = []
    for _ in range(3):
        chars = string.ascii_letters + string.digits + string.punctuation
        high_entropy_samples.append("".join(rng.choice(chars) for _ in range(64)))

    # Very long
    long_samples = [
        "A" * 2000,
        "x" * 1500 + "=" * 500,
    ]

    # Mixed encoding
    mixed_samples = [
        quote("&lt;test&gt;") + "&amp;" + "\\u0041",
        "&#60;" + quote("<encoded>") + "\\x3C",
    ]

    all_pools = [
        cleartext_samples,
        url_encoded_samples,
        [multi_url],
        html_samples,
        unicode_samples,
        json_samples,
        b64_samples,
        ws_samples,
        non_ascii_samples,
        high_entropy_samples,
        long_samples,
        mixed_samples,
    ]

    # Add all curated samples first
    for pool in all_pools:
        payloads.extend(pool)

    # Fill remaining with random picks
    while len(payloads) < count:
        pool = rng.choice(all_pools)
        payloads.append(rng.choice(pool))

    # Truncate to exact count and shuffle
    payloads = payloads[:count]
    rng.shuffle(payloads)

    with open(output, "w", encoding="utf-8") as f:
        for p in payloads:
            f.write(p + "\n")

    click.echo(f"Generated {len(payloads)} synthetic payloads to {output}")
