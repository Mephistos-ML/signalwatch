"""Tests for notification adapters."""

from __future__ import annotations

from typing import Any

import pytest

from signalwatch.app.notifier_factory import create_notifier
from signalwatch.config import NotificationConfig
from signalwatch.models import WatchItem
from signalwatch.notify.formatting import (
    format_log_item_message,
    format_telegram_item_message,
)
from signalwatch.notify.telegram import TelegramNotifier


def test_create_notifier_builds_telegram_notifier_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a Telegram notifier using environment-backed config."""
    monkeypatch.setenv("SIGNALWATCH_TELEGRAM_BOT_TOKEN", "bot-token")
    monkeypatch.setenv("SIGNALWATCH_TELEGRAM_CHAT_ID", "chat-id")

    notifier = create_notifier(
        NotificationConfig(
            type="telegram",
            bot_token_env="SIGNALWATCH_TELEGRAM_BOT_TOKEN",
            chat_id_env="SIGNALWATCH_TELEGRAM_CHAT_ID",
        )
    )

    assert isinstance(notifier, TelegramNotifier)


def test_create_notifier_requires_telegram_env_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject Telegram config when a required environment value is missing."""
    monkeypatch.delenv("SIGNALWATCH_TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("SIGNALWATCH_TELEGRAM_CHAT_ID", "chat-id")

    with pytest.raises(ValueError, match="SIGNALWATCH_TELEGRAM_BOT_TOKEN"):
        create_notifier(
            NotificationConfig(
                type="telegram",
                bot_token_env="SIGNALWATCH_TELEGRAM_BOT_TOKEN",
                chat_id_env="SIGNALWATCH_TELEGRAM_CHAT_ID",
            )
        )


def test_telegram_notifier_posts_new_item_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Send formatted new item messages to Telegram."""
    requests_seen: list[dict[str, Any]] = []

    class FakeResponse:
        """Minimal successful requests response."""

        def raise_for_status(self) -> None:
            """Accept the fake response as successful."""

        def json(self) -> dict[str, bool]:
            """Return a successful Telegram payload."""
            return {"ok": True}

    def fake_post(
        url: str,
        json: dict[str, object],
        timeout: int,
    ) -> FakeResponse:
        requests_seen.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("signalwatch.notify.telegram.requests.post", fake_post)

    notifier = TelegramNotifier(
        bot_token="bot-token",
        chat_id="chat-id",
        timeout_seconds=5,
    )
    notifier.send_new_items(
        [
            WatchItem(
                source="tkmaxx",
                item_id="123",
                title="Gucci & Co - Leather belt",
                url="https://example.com/products/123?colour=black&size=m",
                metadata={
                    "price_gbp": 199.99,
                    "rrp_gbp": 410.0,
                    "saving_gbp": 210.01,
                    "saving_percent": 51.0,
                    "stock_message": "ONLY 1 LEFT",
                    "badge": "Gold Label",
                },
            )
        ]
    )

    assert requests_seen == [
        {
            "url": "https://api.telegram.org/botbot-token/sendMessage",
            "json": {
                "chat_id": "chat-id",
                "text": (
                    "❗ <b>NEW ITEM</b>\n"
                    "\n"
                    "Gucci &amp; Co - Leather belt\n"
                    "💷 £199.99 | RRP £410.00 | Save £210.01 (51%)\n"
                    "⚠️ ONLY 1 LEFT\n"
                    "\n"
                    "https://example.com/products/123?colour=black&amp;size=m"
                ),
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            "timeout": 5,
        }
    ]


def test_notification_formatters_create_compact_item_messages() -> None:
    """Format watch items consistently for log and Telegram notifications."""
    item = WatchItem(
        source="tkmaxx",
        item_id="123",
        title="Gucci & Co - Leather belt",
        url="https://example.com/products/123?colour=black&size=m",
        metadata={
            "price_gbp": 199.99,
            "rrp_gbp": 410.0,
            "saving_gbp": 210.01,
            "saving_percent": 51.0,
            "stock_message": "ONLY 1 LEFT",
            "badge": "Gold Label",
        },
    )

    assert format_log_item_message(item) == (
        "New item: Gucci & Co - Leather belt | "
        "£199.99 | RRP £410.00 | Save £210.01 (51%) | "
        "https://example.com/products/123?colour=black&size=m"
    )
    assert format_telegram_item_message(item) == (
        "❗ <b>NEW ITEM</b>\n"
        "\n"
        "Gucci &amp; Co - Leather belt\n"
        "💷 £199.99 | RRP £410.00 | Save £210.01 (51%)\n"
        "⚠️ ONLY 1 LEFT\n"
        "\n"
        "https://example.com/products/123?colour=black&amp;size=m"
    )
