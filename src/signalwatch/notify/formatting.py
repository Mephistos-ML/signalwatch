"""Notification message formatting helpers."""

from __future__ import annotations

from html import escape

from signalwatch.models import WatchItem


def format_log_item_message(item: WatchItem) -> str:
    """Format a watch item as a compact one-line log message.

    Args:
        item: Watch item to format.

    Returns:
        One-line notification log message.
    """
    price_line = _format_price_line(item)
    if price_line is None:
        return f"New item: {item.title} | {item.url}"

    return f"New item: {item.title} | {price_line} | {item.url}"


def format_telegram_item_message(item: WatchItem) -> str:
    """Format a watch item as a compact Telegram message.

    Args:
        item: Watch item to format.

    Returns:
        Multi-line Telegram notification message.
    """
    lines = ["❗ <b>NEW ITEM</b>", "", escape(item.title)]

    price_line = _format_price_line(item)
    if price_line is not None:
        lines.append(f"💷 {escape(price_line)}")

    stock_message = _get_string_metadata(item=item, key="stock_message")
    if stock_message is not None:
        lines.append(f"⚠️ {escape(stock_message)}")

    lines.extend(["", escape(item.url)])

    return "\n".join(lines)


def _format_price_line(item: WatchItem) -> str | None:
    """Format available price, RRP, and saving metadata.

    Args:
        item: Watch item with metadata.

    Returns:
        Compact price line, or None if no price metadata is available.
    """
    parts: list[str] = []

    price = _format_gbp(item.metadata.get("price_gbp"))
    if price is not None:
        parts.append(price)

    rrp = _format_gbp(item.metadata.get("rrp_gbp"))
    if rrp is not None:
        parts.append(f"RRP {rrp}")

    saving = _format_saving(item)
    if saving is not None:
        parts.append(saving)

    if not parts:
        return None

    return " | ".join(parts)


def _format_saving(item: WatchItem) -> str | None:
    """Format saving metadata.

    Args:
        item: Watch item with metadata.

    Returns:
        Formatted saving, or None if unavailable.
    """
    saving_gbp = _format_gbp(item.metadata.get("saving_gbp"))
    saving_percent = _format_percent(item.metadata.get("saving_percent"))

    if saving_gbp is None and saving_percent is None:
        return None

    if saving_gbp is None:
        return f"Save {saving_percent}"

    if saving_percent is None:
        return f"Save {saving_gbp}"

    return f"Save {saving_gbp} ({saving_percent})"


def _format_gbp(value: object) -> str | None:
    """Format a GBP metadata value.

    Args:
        value: Raw metadata value.

    Returns:
        Formatted GBP value, or None if the value is not numeric.
    """
    if isinstance(value, int | float):
        return f"£{value:.2f}"

    return None


def _format_percent(value: object) -> str | None:
    """Format a percentage metadata value.

    Args:
        value: Raw metadata value.

    Returns:
        Formatted percentage, or None if the value is not numeric.
    """
    if isinstance(value, int | float):
        return f"{value:g}%"

    return None


def _get_string_metadata(item: WatchItem, key: str) -> str | None:
    """Read a non-empty string metadata value.

    Args:
        item: Watch item with metadata.
        key: Metadata key.

    Returns:
        Metadata string, or None if missing or blank.
    """
    value = item.metadata.get(key)
    if not isinstance(value, str):
        return None

    value = value.strip()
    if not value:
        return None

    return value
