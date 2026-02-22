# CorpusLab

Security payload corpus management CLI tool. Normalize storage, detect encoding patterns, classify payloads, cluster duplicates, and generate deterministic reports.

## Requirements

- **Python 3.9+** (check with `python3 --version`)
- **pip** (check with `pip3 --version`)
- **git** (to clone the repository)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/muhammetuslu78/corpuslab.git
cd corpuslab
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

You should see `(.venv)` at the beginning of your terminal prompt.

### 3. Install CorpusLab

For regular usage:

```bash
pip install -e .
```

For development (includes pytest, ruff, mypy):

```bash
pip install -e ".[dev]"
```

### 4. Verify the installation

```bash
corpuslab --version
# Expected output: corpuslab, version 0.1.0
```

Or run with the Python module syntax:

```bash
python -m corpuslab --version
```

### 5. (Optional) Run the test suite

```bash
pytest tests/ -v
# Expected: 128 passed
```

### Uninstall

```bash
pip uninstall corpuslab
```

To also remove the virtual environment:

```bash
deactivate
rm -rf .venv
```

## Quick Start

```bash
# Generate synthetic test payloads
corpuslab generate -n 200 -o payloads.txt

# Import payloads into a corpus
corpuslab import payloads.txt -o corpus.jsonl

# View corpus statistics
corpuslab summarize corpus.jsonl

# Cluster by canonical fingerprint
corpuslab cluster corpus.jsonl -o corpus_clustered.jsonl

# Generate a Markdown report
corpuslab report corpus_clustered.jsonl -o report.md

# Filter by tag
corpuslab filter corpus.jsonl --tag url_encoded --tag html_entities

# Export to CSV
corpuslab export corpus.jsonl --format csv -o export.csv
```

## Commands

| Command | Description |
|---------|-------------|
| `import` | Ingest payloads from text/CSV/JSON/JSONL files |
| `summarize` | Show corpus statistics and tag distribution |
| `filter` | Query and filter records by tags, length, confidence |
| `cluster` | Group payloads by fingerprint similarity |
| `report` | Generate a Markdown analysis report |
| `export` | Export corpus to JSONL, CSV, or Markdown |
| `generate` | Create synthetic non-malicious test payloads |

## Supported Input Formats

- **Plain text** — one payload per line
- **CSV** — specify payload column with `--field`
- **JSON** — arrays of strings or objects
- **JSONL / NDJSON** — one JSON object per line

Format is auto-detected by extension and content heuristics, or can be specified with `--format`.

## Tag Taxonomy

Each payload is classified with one or more representation/encoding tags:

| Tag | Description |
|-----|-------------|
| `cleartext` | All printable ASCII, no encoding markers |
| `url_encoded` | Contains `%XX` sequences |
| `multi_url_encoded` | 2+ layers of URL encoding |
| `html_entities` | Contains `&amp;`, `&#NNN;`, `&#xHH;` entities |
| `unicode_escapes` | Contains `\uXXXX`, `\xNN` sequences |
| `json_escaped` | Contains JSON escape sequences (`\"`, `\\n`) |
| `base64_like` | Contains base64-decodable segments |
| `mixed_encoding` | 2+ encoding types detected |
| `whitespace_obfuscation` | Unusual whitespace patterns |
| `non_ascii` | Contains non-ASCII characters |
| `high_entropy` | Shannon entropy above threshold |
| `very_long_input` | Length exceeds threshold (default: 1024) |

Each tag includes a confidence score (0-1) and rationale.

## Privacy & Redaction

Payloads may contain secrets or PII. Use `--redact` during import:

```bash
corpuslab import payloads.txt -o corpus.jsonl --redact
```

Built-in patterns mask: emails, JWTs, bearer tokens, API keys, IPv4 addresses.

Add custom patterns:
```bash
corpuslab import payloads.txt -o corpus.jsonl --redact --redact-pattern "SECRET_\w+"
```

## Architecture

- **Streaming pipeline** — generators throughout; constant memory regardless of input size
- **JSONL storage** — no database dependency; appendable, diffable, human-readable
- **Deterministic** — same input + same config = identical outputs
- **Minimal deps** — only `click` and `pydantic` at runtime

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=corpuslab --cov-report=term-missing

# Run performance benchmark
pytest tests/test_integration/test_performance.py -v
```

## How to Use Safely

1. **Never commit raw corpus files** — they may contain sensitive payloads
2. **Use `--redact` mode** for any corpus that may contain PII/secrets
3. **Review reports before sharing** — even redacted reports may reveal patterns
4. **Use `--redacted` flag** when generating reports for external consumption
5. **Keep corpus files local** — treat them as sensitive security data
