"""Base source protocol."""

from __future__ import annotations

from collections.abc import Sequence

from typing import Protocol

from signalwatch.models import WatchItem

class Source(Protocol):
    """Protocol implemented by all item sources."""

    def fetch_items(self) -> Sequence[WatchItem]:
        """Fetch and normalise items from the source.

        Returns:
            Normalised watch items extracted from the source.
        """
        ...