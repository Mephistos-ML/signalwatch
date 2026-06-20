"""Long-running watch workflow."""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Protocol

from signalwatch.app.run_bot import run_bot
from signalwatch.config import PollingConfig, load_config

logger = logging.getLogger(__name__)


class Sleeper(Protocol):
    """Callable sleep function used by the watch loop."""

    def __call__(self, seconds: float) -> None:
        """Sleep for the requested number of seconds."""


def watch(config_path: Path, sleep: Sleeper = time.sleep) -> None:
    """Run the bot repeatedly using polling config.

    Args:
        config_path: Path to the YAML configuration file.
        sleep: Sleep callable, injectable for tests.
    """
    config = load_config(config_path)
    logger.info(
        "Watching with interval=%ds jitter=%ds",
        config.polling.interval_seconds,
        config.polling.jitter_seconds,
    )

    while True:
        try:
            run_bot(config_path)
        except Exception:
            logger.exception("Monitoring cycle failed")

        delay_seconds = calculate_next_delay_seconds(config.polling)
        logger.info("Next monitoring cycle in %.0f second(s)", delay_seconds)

        try:
            sleep(delay_seconds)
        except KeyboardInterrupt:
            logger.info("Watch stopped")
            return


def calculate_next_delay_seconds(polling_config: PollingConfig) -> float:
    """Calculate the next polling delay with random jitter.

    Args:
        polling_config: Polling configuration.

    Returns:
        Delay in seconds. The value is never lower than one second.
    """
    jitter = random.uniform(
        -polling_config.jitter_seconds,
        polling_config.jitter_seconds,
    )

    return max(1.0, polling_config.interval_seconds + jitter)
