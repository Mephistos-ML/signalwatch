"""Tests for long-running watch configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from signalwatch.app.watch import calculate_next_delay_seconds
from signalwatch.config import PollingConfig, load_config


def test_load_config_parses_polling_config(tmp_path: Path) -> None:
    """Parse polling interval and jitter from YAML config."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
source:
  type: fake

storage:
  sqlite_path: "signalwatch.sqlite3"

notification:
  type: log

polling:
  interval_seconds: 3600
  jitter_seconds: 600
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.polling == PollingConfig(
        interval_seconds=3600,
        jitter_seconds=600,
    )


def test_load_config_uses_default_polling_config(tmp_path: Path) -> None:
    """Use hourly polling defaults when polling config is omitted."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
source:
  type: fake

storage:
  sqlite_path: "signalwatch.sqlite3"

notification:
  type: log
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.polling == PollingConfig(
        interval_seconds=3600,
        jitter_seconds=600,
    )


def test_calculate_next_delay_seconds_adds_random_jitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Add random jitter to the configured polling interval."""
    monkeypatch.setattr("signalwatch.app.watch.random.uniform", lambda _a, _b: 42.0)

    delay_seconds = calculate_next_delay_seconds(
        PollingConfig(interval_seconds=3600, jitter_seconds=600)
    )

    assert delay_seconds == 3642.0


def test_calculate_next_delay_seconds_never_returns_less_than_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clamp polling delay to at least one second."""
    monkeypatch.setattr("signalwatch.app.watch.random.uniform", lambda _a, _b: -600.0)

    delay_seconds = calculate_next_delay_seconds(
        PollingConfig(interval_seconds=10, jitter_seconds=600)
    )

    assert delay_seconds == 1.0
