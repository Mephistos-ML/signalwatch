

"""Run-bot application workflow."""

from __future__ import annotations

import logging
from pathlib import Path

from signalwatch.app.notifier_factory import create_notifier
from signalwatch.app.source_factory import create_source
from signalwatch.config import load_config
from signalwatch.matching import filter_matching_items
from signalwatch.storage.sqlite import load_seen_item_ids, upsert_items

logger = logging.getLogger(__name__)


def run_bot(config_path: Path) -> None:
    """Run one monitoring cycle from a YAML configuration file.

    Args:
        config_path: Path to the YAML configuration file.
    """
    logger.info("Using config: %s", config_path)

    config = load_config(config_path)
    logger.info("Source type: %s", config.source.type)

    source = create_source(config.source)
    notifier = create_notifier(config.notification)

    items = source.fetch_items()
    seen_item_ids = load_seen_item_ids(
        db_path=config.storage.sqlite_path,
        source=config.source.type,
    )
    new_items = [item for item in items if item.item_id not in seen_item_ids]
    matched_new_items = filter_matching_items(
        items=new_items,
        matching_config=config.matching,
    )

    logger.info("Fetched %d item(s)", len(items))
    logger.info("Found %d new item(s)", len(new_items))
    logger.info("Matched %d new item(s)", len(matched_new_items))

    notifier.send_new_items(matched_new_items)
    upsert_items(db_path=config.storage.sqlite_path, items=items)
