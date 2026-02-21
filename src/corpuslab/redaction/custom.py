"""User-defined regex pattern compilation."""

from __future__ import annotations

import re
from typing import List


def compile_user_patterns(pattern_strings: List[str]) -> List[re.Pattern]:
    """Compile user-provided regex strings. Raises ValueError on invalid patterns."""
    patterns = []
    for ps in pattern_strings:
        try:
            patterns.append(re.compile(ps))
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{ps}': {e}") from e
    return patterns
