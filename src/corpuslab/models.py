"""Pydantic models for CorpusLab records."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TagName(str, Enum):
    CLEARTEXT = "cleartext"
    URL_ENCODED = "url_encoded"
    MULTI_URL_ENCODED = "multi_url_encoded"
    HTML_ENTITIES = "html_entities"
    UNICODE_ESCAPES = "unicode_escapes"
    JSON_ESCAPED = "json_escaped"
    BASE64_LIKE = "base64_like"
    MIXED_ENCODING = "mixed_encoding"
    WHITESPACE_OBFUSCATION = "whitespace_obfuscation"
    NON_ASCII = "non_ascii"
    HIGH_ENTROPY = "high_entropy"
    VERY_LONG_INPUT = "very_long_input"


class TagResult(BaseModel):
    tag: TagName
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    features: Dict[str, Any] = Field(default_factory=dict)


class TransformStep(BaseModel):
    name: str
    input_len: int
    output_len: int
    changed: bool
    stop_reason: Optional[str] = None


class CanonicalView(BaseModel):
    name: str
    value: str
    trace: List[TransformStep] = Field(default_factory=list)


class Fingerprints(BaseModel):
    raw_sha256: str
    canonical_sha256_nfkc: str
    canonical_sha256_url_decoded: str
    canonical_sha256_html_decoded: str
    length_bucket: str
    structure_hash: str


class IngestMetadata(BaseModel):
    source_file: Optional[str] = None
    source_format: str
    line_number: Optional[int] = None
    field_name: Optional[str] = None
    byte_offset: Optional[int] = None
    environment: Optional[str] = None
    collection_method: Optional[str] = None
    ingested_at: Optional[str] = None


class PayloadRecord(BaseModel):
    id: str
    raw: str
    raw_length: int
    tags: List[TagResult] = Field(default_factory=list)
    canonical_views: List[CanonicalView] = Field(default_factory=list)
    fingerprints: Optional[Fingerprints] = None
    cluster_id: Optional[str] = None
    ingest_meta: IngestMetadata
    redacted_raw: Optional[str] = None
