"""Command-line interface for SignalWatch."""

from __future__ import annotations

import argparse
from pathlib import Path

from signalwatch.app.run_bot import run_bot
from signalwatch.app.watch import watch
from signalwatch.logging_config import setup_logging


def build_parser() -> argparse.ArgumentParser:
    """Build the SignalWatch command-line parser."""
    parser = argparse.ArgumentParser(
        prog="signalwatch",
        description="Configurable monitoring and alerting engine for domain-specific signals.",
        epilog=(
            "Examples:\n"
            "  signalwatch check examples/example.yml\n"
            "  signalwatch watch examples/tkmaxx-telegram.yml\n"
            "  signalwatch --verbose check examples/example.yml\n"
            "  signalwatch --quiet check examples/example.yml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show errors and critical failures.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        metavar="COMMAND",
    )

    check_parser = subparsers.add_parser(
        "check",
        help="Run one monitoring cycle from a YAML config file.",
        description="Run one monitoring cycle using source, storage, and notification settings from YAML.",
        epilog=(
            "Examples:\n"
            "  signalwatch check examples/example.yml\n"
            "  signalwatch --verbose check examples/example.yml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    check_parser.add_argument(
        "config_path",
        type=Path,
        help="Path to the YAML configuration file that defines the monitoring run.",
    )

    watch_parser = subparsers.add_parser(
        "watch",
        help="Run monitoring cycles repeatedly from a YAML config file.",
        description="Run monitoring cycles repeatedly using polling settings from YAML.",
        epilog=(
            "Examples:\n"
            "  signalwatch watch examples/tkmaxx-telegram.yml\n"
            "  signalwatch --verbose watch examples/tkmaxx-telegram.yml"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    watch_parser.add_argument(
        "config_path",
        type=Path,
        help="Path to the YAML configuration file that defines the watcher.",
    )

    return parser


def main() -> None:
    """Run the SignalWatch command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(verbose=args.verbose, quiet=args.quiet)

    if args.command == "check":
        run_bot(args.config_path)
        return

    if args.command == "watch":
        watch(args.config_path)
        return

    parser.error(f"Unsupported command: {args.command}")
