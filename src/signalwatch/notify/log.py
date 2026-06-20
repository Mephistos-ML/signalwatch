"""Logging notifier implementation."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from signalwatch.models import WatchItem
from signalwatch.notify.formatting import format_log_item_message

logger = logging.getLogger(__name__)


class LogNotifier:
    """Notifier that writes newly discovered items to logs."""

    def send_new_items(self, items: Sequence[WatchItem]) -> None:
        """Log newly discovered items.

        Args:
            items: Newly discovered watch items.
        """
        for item in items:
            logger.info(format_log_item_message(item))
