"""Abstract base class for payload detectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from corpuslab.models import TagResult


class BaseDetector(ABC):
    @abstractmethod
    def detect(self, raw: str) -> List[TagResult]:
        """Return zero or more TagResults for the given raw payload."""
