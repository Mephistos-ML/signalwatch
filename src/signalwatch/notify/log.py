"""Logging notifier implementation."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from signalwatch.models import WatchItem

logger = logging.getLogger(__name__)


class LogNotifier:
    """Notifier that writes newly discovered items to logs."""

    def send_new_items(self, items: Sequence[WatchItem]) -> None:
        """Log newly discovered items.

        Args:
            items: Newly discovered watch items.
        """
        for item in items:
            price = _format_price(item.metadata.get("price_gbp"))
            if price is None:
                logger.info("New item: %s | %s", item.title, item.url)
            else:
                logger.info("New item: %s | %s | %s", item.title, price, item.url)


def _format_price(value: object) -> str | None:
    """Format a GBP price value for notification logs.

    Args:
        value: Raw metadata value.

    Returns:
        Formatted GBP price, or None if the value is not numeric.
    """
    if isinstance(value, int | float):
        return f"£{value:.2f}"

    return None
