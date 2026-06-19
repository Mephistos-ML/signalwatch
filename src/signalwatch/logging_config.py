"""Configure command-line logging behaviour."""

from __future__ import annotations

import logging
import sys


class ColorFormatter(logging.Formatter):
    """Minimal ANSI colour formatter for console output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with conservative level-based colour."""
        message = super().format(record)

        if record.levelno == logging.DEBUG:
            return f"\033[90m{message}\033[0m"
        if record.levelno == logging.INFO:
            return f"\033[36m{message}\033[0m"
        if record.levelno == logging.WARNING:
            return f"\033[33m{message}\033[0m"
        if record.levelno >= logging.ERROR:
            return f"\033[31m{message}\033[0m"

        return message


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """Configure root logging for command-line execution.

    Args:
        verbose: Enable debug-level logging.
        quiet: Only show errors and critical failures.
    """
    level = logging.INFO

    if verbose:
        level = logging.DEBUG
    if quiet:
        level = logging.ERROR

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColorFormatter("%(levelname)s - %(message)s"))

    root.addHandler(handler)