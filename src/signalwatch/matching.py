"""Item matching rules."""

from __future__ import annotations

from collections.abc import Sequence

from signalwatch.config import MatchingConfig
from signalwatch.models import WatchItem


def filter_matching_items(
    items: Sequence[WatchItem],
    matching_config: MatchingConfig,
) -> list[WatchItem]:
    """Filter items according to matching configuration.

    Args:
        items: Watch items to filter.
        matching_config: Item matching configuration.

    Returns:
        Items that match the configured rules.
    """
    if not matching_config.brands:
        return list(items)

    wanted_brands = {brand.casefold() for brand in matching_config.brands}
    return [item for item in items if _matches_brand(item, wanted_brands)]


def _matches_brand(item: WatchItem, wanted_brands: set[str]) -> bool:
    """Return whether an item matches one of the configured brands.

    Args:
        item: Watch item to inspect.
        wanted_brands: Case-folded brand names to match.

    Returns:
        True when the item brand matches a wanted brand.
    """
    brand = _get_item_brand(item)
    if brand is None:
        return False

    return brand.casefold() in wanted_brands


def _get_item_brand(item: WatchItem) -> str | None:
    """Read a non-empty item brand from metadata.

    Args:
        item: Watch item to inspect.

    Returns:
        Item brand, or None if unavailable.
    """
    brand = item.metadata.get("brand")
    if not isinstance(brand, str):
        return None

    brand = brand.strip()
    if not brand:
        return None

    return brand
