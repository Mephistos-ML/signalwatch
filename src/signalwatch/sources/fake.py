"""Fake source used to test the pipeline without network access."""

from __future__ import annotations

from collections.abc import Sequence

from signalwatch.models import WatchItem


class FakeSource:
    """Source returning static items for local pipeline testing."""

    def fetch_items(self) -> Sequence[WatchItem]:
        """Return static test items."""
        return [
            WatchItem(
                source="fake",
                item_id="fake-001",
                title="Balenciaga Test Jacket",
                url="https://example.com/fake-001",
                metadata={
                    "brand": "Balenciaga",
                    "price_gbp": 199.99,
                    "size": "M",
                },
            )
        ]