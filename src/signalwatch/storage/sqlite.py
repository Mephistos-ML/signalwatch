"""SQLite storage for seen watch items."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from signalwatch.models import WatchItem


def init_db(db_path: Path) -> None:
    """Initialise the SQLite database schema.

    Args:
        db_path: Path to the SQLite database file.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_items (
                source TEXT NOT NULL,
                item_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                PRIMARY KEY (source, item_id)
            )
            """
        )


def load_seen_item_ids(db_path: Path, source: str) -> set[str]:
    """Load item IDs already seen for a source.

    Args:
        db_path: Path to the SQLite database file.
        source: Source name to filter by.

    Returns:
        Set of item IDs already present in storage for the source.
    """
    init_db(db_path)

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT item_id
            FROM seen_items
            WHERE source = ?
            """,
            (source,),
        )

        return {row[0] for row in rows}


def upsert_items(db_path: Path, items: Sequence[WatchItem]) -> None:
    """Insert or update seen watch items.

    Existing rows keep their original ``first_seen_at`` value and receive an
    updated ``last_seen_at`` value.

    Args:
        db_path: Path to the SQLite database file.
        items: Watch items to persist.
    """
    init_db(db_path)

    seen_at = _utc_now_iso()
    rows = [
        (
            item.source,
            item.item_id,
            item.title,
            item.url,
            seen_at,
            seen_at,
            json.dumps(item.metadata, ensure_ascii=False, sort_keys=True),
        )
        for item in items
    ]

    with sqlite3.connect(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO seen_items (
                source,
                item_id,
                title,
                url,
                first_seen_at,
                last_seen_at,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, item_id) DO UPDATE SET
                title = excluded.title,
                url = excluded.url,
                last_seen_at = excluded.last_seen_at,
                metadata_json = excluded.metadata_json
            """,
            rows,
        )


def _utc_now_iso() -> str:
    """Return the current UTC time in ISO 8601 format."""
    return datetime.now(UTC).isoformat()
