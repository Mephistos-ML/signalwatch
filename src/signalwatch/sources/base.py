"""Base interface for source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from signalwatch.models import WatchItem


class SourceAdapter(ABC):
    """Base interface for monitored data sources."""

    @abstractmethod
    def fetch_items(self) -> Sequence[WatchItem]:
        """Fetch and normalise items from the source.

        Returns:
            Normalised watch items extracted from the source.
        """
        raise NotImplementedError