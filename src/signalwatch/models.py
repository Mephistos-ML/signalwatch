"""Domain models used by the monitoring pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WatchItem:
    """Generic item extracted from a monitored source.

    Attributes:
        source: Source name, such as "tkmaxx".
        item_id: Stable source-specific item identifier.
        title: Human-readable item title.
        url: Canonical item URL.
        metadata: Source-specific structured metadata.
    """

    source: str
    item_id: str
    title: str
    url: str
    metadata: dict[str, Any]