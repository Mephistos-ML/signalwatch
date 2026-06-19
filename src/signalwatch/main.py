"""Command-line entry point for SignalWatch."""

from __future__ import annotations

import logging

from signalwatch.adapters.fake import FakeAdapter
from signalwatch.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Run a minimal local pipeline."""
    setup_logging(verbose=True)

    adapter = FakeAdapter()
    items = adapter.fetch_items()

    logger.info("Fetched %d item(s)", len(items))

    for item in items:
        logger.info("%s | %s | %s", item.source, item.title, item.url)
        logger.debug("Metadata: %s", item.metadata)


if __name__ == "__main__":
    main()