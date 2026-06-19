"""Application-level monitoring pipeline for SignalWatch."""

from __future__ import annotations

import logging
from pathlib import Path

from signalwatch.sources.fake import FakeAdapter

logger = logging.getLogger(__name__)


def run_bot(config_path: Path) -> None:
    """Run one monitoring cycle from a YAML configuration file.

    Args:
        config_path: Path to the YAML configuration file.
    """
    logger.info("Using config: %s", config_path)

    # Temporary smoke test. This will later be replaced by config-driven
    # adapter construction, storage, and notification dispatch.
    adapter = FakeAdapter()
    items = adapter.fetch_items()

    logger.info("Fetched %d item(s)", len(items))

    for item in items:
        logger.info("%s | %s | %s", item.source, item.title, item.url)
        logger.debug("Metadata: %s", item.metadata)
