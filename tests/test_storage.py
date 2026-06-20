"""Tests for SQLite item storage."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from signalwatch.models import WatchItem
from signalwatch.storage.sqlite import load_seen_item_ids, upsert_items


def test_upsert_items_persists_watch_items(tmp_path: Path) -> None:
    """Persist a watch item with its core fields and metadata."""
    db_path = tmp_path / "signalwatch.sqlite3"
    item = WatchItem(
        source="tkmaxx",
        item_id="123",
        title="Gucci - Leather belt",
        url="https://example.com/products/123",
        metadata={
            "brand": "Gucci",
            "price_gbp": 199.99,
            "stock_message": "ONLY 1 LEFT",
        },
    )

    upsert_items(db_path=db_path, items=[item])

    row = _fetch_seen_item(db_path=db_path, source="tkmaxx", item_id="123")

    assert row["source"] == "tkmaxx"
    assert row["item_id"] == "123"
    assert row["title"] == "Gucci - Leather belt"
    assert row["url"] == "https://example.com/products/123"
    assert json.loads(row["metadata_json"]) == {
        "brand": "Gucci",
        "price_gbp": 199.99,
        "stock_message": "ONLY 1 LEFT",
    }


def test_load_seen_item_ids_filters_by_source(tmp_path: Path) -> None:
    """Load only item IDs belonging to the requested source."""
    db_path = tmp_path / "signalwatch.sqlite3"
    upsert_items(
        db_path=db_path,
        items=[
            WatchItem(
                source="tkmaxx",
                item_id="tk-1",
                title="Tk Maxx item",
                url="https://example.com/tk-1",
                metadata={},
            ),
            WatchItem(
                source="fake",
                item_id="fake-1",
                title="Fake item",
                url="https://example.com/fake-1",
                metadata={},
            ),
        ],
    )

    assert load_seen_item_ids(db_path=db_path, source="tkmaxx") == {"tk-1"}
    assert load_seen_item_ids(db_path=db_path, source="fake") == {"fake-1"}


def test_upsert_items_updates_existing_item_without_duplicate(
    tmp_path: Path,
) -> None:
    """Update an existing item without creating duplicate rows."""
    db_path = tmp_path / "signalwatch.sqlite3"
    upsert_items(
        db_path=db_path,
        items=[
            WatchItem(
                source="tkmaxx",
                item_id="123",
                title="Old title",
                url="https://example.com/old",
                metadata={"price_gbp": 299.99},
            )
        ],
    )

    upsert_items(
        db_path=db_path,
        items=[
            WatchItem(
                source="tkmaxx",
                item_id="123",
                title="New title",
                url="https://example.com/new",
                metadata={"price_gbp": 199.99},
            )
        ],
    )

    row_count = _count_seen_items(db_path=db_path)
    row = _fetch_seen_item(db_path=db_path, source="tkmaxx", item_id="123")

    assert row_count == 1
    assert row["title"] == "New title"
    assert row["url"] == "https://example.com/new"
    assert json.loads(row["metadata_json"]) == {"price_gbp": 199.99}
    assert row["first_seen_at"] <= row["last_seen_at"]


def _fetch_seen_item(db_path: Path, source: str, item_id: str) -> dict[str, object]:
    """Fetch one stored item row as a dictionary."""
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT
                source,
                item_id,
                title,
                url,
                first_seen_at,
                last_seen_at,
                metadata_json
            FROM seen_items
            WHERE source = ? AND item_id = ?
            """,
            (source, item_id),
        ).fetchone()

    assert row is not None
    return dict(row)


def _count_seen_items(db_path: Path) -> int:
    """Count stored seen item rows."""
    with sqlite3.connect(db_path) as connection:
        row = connection.execute("SELECT COUNT(*) FROM seen_items").fetchone()

    assert row is not None
    return int(row[0])
