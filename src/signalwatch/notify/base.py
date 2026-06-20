"""Notification interfaces."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from signalwatch.models import WatchItem


class Notifier(Protocol):
    """Sends notifications about watch items."""

    def send_new_items(self, items: Sequence[WatchItem]) -> None:
        """Send notifications for newly discovered items.

        Args:
            items: Newly discovered watch items.
        """
