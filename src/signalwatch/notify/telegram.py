"""Telegram notifier implementation."""

from __future__ import annotations

from collections.abc import Sequence

import requests

from signalwatch.models import WatchItem
from signalwatch.notify.formatting import format_telegram_item_message

DEFAULT_TIMEOUT_SECONDS = 15


class TelegramNotifier:
    """Notifier that sends newly discovered items to a Telegram chat."""

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Initialise the Telegram notifier.

        Args:
            bot_token: Telegram bot token.
            chat_id: Telegram chat ID.
            timeout_seconds: HTTP request timeout in seconds.
        """
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._timeout_seconds = timeout_seconds

    def send_new_items(self, items: Sequence[WatchItem]) -> None:
        """Send newly discovered items to Telegram.

        Args:
            items: Newly discovered watch items.
        """
        for item in items:
            self._send_message(format_telegram_item_message(item))

    def _send_message(self, text: str) -> None:
        """Send one Telegram text message.

        Args:
            text: Message body.

        Raises:
            requests.HTTPError: If Telegram returns an HTTP error response.
            requests.RequestException: If the request fails.
            ValueError: If Telegram returns a non-ok JSON response.
        """
        response = requests.post(
            f"https://api.telegram.org/bot{self._bot_token}/sendMessage",
            json={
                "chat_id": self._chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict) or payload.get("ok") is not True:
            raise ValueError(f"Telegram sendMessage failed: {payload}")
