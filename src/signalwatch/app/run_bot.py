

"""Run-bot application workflow."""

from __future__ import annotations

import logging
from pathlib import Path

from signalwatch.app.source_factory import create_source
from signalwatch.config import load_config

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
    items = source.fetch_items()

    logger.info("Fetched %d item(s)", len(items))

    for item in items:
        logger.info("%s | %s | %s", item.source, item.title, item.url)
        logger.debug("Metadata: %s", item.metadata)