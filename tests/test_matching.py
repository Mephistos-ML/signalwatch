"""Tests for item matching rules."""

from __future__ import annotations

from pathlib import Path

from signalwatch.config import MatchingConfig, load_config
from signalwatch.matching import filter_matching_items
from signalwatch.models import WatchItem


def test_filter_matching_items_matches_brands_case_insensitively() -> None:
    """Match configured brands regardless of case."""
    items = [
        _make_item(item_id="1", brand="balenciaga"),
        _make_item(item_id="2", brand="RICK OWENS"),
        _make_item(item_id="3", brand="Prada"),
    ]

    matched_items = filter_matching_items(
        items=items,
        matching_config=MatchingConfig(brands=("Balenciaga", "Rick Owens")),
    )

    assert [item.item_id for item in matched_items] == ["1", "2"]


def test_filter_matching_items_matches_all_when_no_brands_configured() -> None:
    """Match all items when no brand filter is configured."""
    items = [
        _make_item(item_id="1", brand="Balenciaga"),
        _make_item(item_id="2", brand="Prada"),
    ]

    assert filter_matching_items(items=items, matching_config=MatchingConfig()) == items


def test_filter_matching_items_rejects_missing_brand_when_brands_configured() -> None:
    """Do not match unbranded items when a brand filter is configured."""
    items = [
        _make_item(item_id="1", brand="Balenciaga"),
        WatchItem(
            source="tkmaxx",
            item_id="2",
            title="Unknown item",
            url="https://example.com/2",
            metadata={},
        ),
    ]

    matched_items = filter_matching_items(
        items=items,
        matching_config=MatchingConfig(brands=("Balenciaga",)),
    )

    assert [item.item_id for item in matched_items] == ["1"]


def test_load_config_parses_matching_brands(tmp_path: Path) -> None:
    """Parse matching brands from YAML config."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
source:
  type: fake

storage:
  sqlite_path: "signalwatch.sqlite3"

notification:
  type: log

matching:
  brands:
    - Balenciaga
    - Rick Owens
    - Palm Angels
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.matching.brands == ("Balenciaga", "Rick Owens", "Palm Angels")


def _make_item(item_id: str, brand: str) -> WatchItem:
    """Build a watch item for matching tests."""
    return WatchItem(
        source="tkmaxx",
        item_id=item_id,
        title=f"{brand} item",
        url=f"https://example.com/{item_id}",
        metadata={"brand": brand},
    )
