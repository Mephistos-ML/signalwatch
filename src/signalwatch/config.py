"""Configuration loading for SignalWatch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SourceConfig:
    """Source configuration loaded from YAML."""

    type: str
    url: str | None = None


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from YAML."""

    source: SourceConfig


def load_config(path: Path) -> AppConfig:
    """Load application configuration from a YAML file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Parsed application configuration.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If the config file is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file does not exist: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw_config: dict[str, Any] | None = yaml.safe_load(handle)

    if not isinstance(raw_config, dict):
        raise ValueError("Config file must contain a YAML mapping.")

    source = raw_config.get("source")
    if not isinstance(source, dict):
        raise ValueError("Config file must define a 'source' mapping.")

    source_type = source.get("type")
    if not isinstance(source_type, str) or not source_type:
        raise ValueError("Config source must define a non-empty 'type' string.")

    source_url = source.get("url")
    if source_url is not None and not isinstance(source_url, str):
        raise ValueError("Config source 'url' must be a string if provided.")

    return AppConfig(
        source=SourceConfig(
            type=source_type,
            url=source_url,
        )
    )