"""Transformation trace recording."""

from __future__ import annotations

from typing import Callable, Optional, Tuple

from corpuslab.models import TransformStep


def traced_transform(
    name: str,
    fn: Callable[[str], str],
    input_str: str,
    stop_reason: Optional[str] = None,
) -> Tuple[str, TransformStep]:
    """Apply a transform and record a trace step."""
    output = fn(input_str)
    step = TransformStep(
        name=name,
        input_len=len(input_str),
        output_len=len(output),
        changed=(output != input_str),
        stop_reason=stop_reason,
    )
    return output, step
