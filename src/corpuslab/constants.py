"""Shared constants, thresholds, and configuration defaults."""

# Tagging thresholds
DEFAULT_HIGH_ENTROPY_THRESHOLD = 4.5
DEFAULT_VERY_LONG_THRESHOLD = 1024
DEFAULT_MIN_CONFIDENCE_DISPLAY = 0.3

# Base64 detection
BASE64_MIN_LENGTH = 20
BASE64_PADDING_BONUS = 0.15

# URL encoding detection
URL_ENCODED_MIN_RATIO = 0.05

# Canonical view config
MAX_URL_DECODE_DEPTH = 10

# Length buckets for fingerprinting
LENGTH_BUCKETS = [
    (64, "0-64"),
    (256, "65-256"),
    (1024, "257-1024"),
]
LENGTH_BUCKET_OVERFLOW = "1025+"

# Redaction
REDACTION_PLACEHOLDER = "[REDACTED]"

# Display
MAX_DISPLAY_LENGTH = 200
