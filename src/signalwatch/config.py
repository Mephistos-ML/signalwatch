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
class StorageConfig:
    """Storage configuration loaded from YAML."""

    sqlite_path: Path


@dataclass(frozen=True)
class NotificationConfig:
    """Notification configuration loaded from YAML."""

    type: str
    bot_token_env: str | None = None
    chat_id_env: str | None = None


@dataclass(frozen=True)
class MatchingConfig:
    """Item matching configuration loaded from YAML."""

    brands: tuple[str, ...] = ()


@dataclass(frozen=True)
class PollingConfig:
    """Polling configuration loaded from YAML."""

    interval_seconds: int = 3600
    jitter_seconds: int = 600


@dataclass(frozen=True)
class AppConfig:
    """Application configuration loaded from YAML."""

    source: SourceConfig
    storage: StorageConfig
    notification: NotificationConfig
    matching: MatchingConfig
    polling: PollingConfig


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

    storage = raw_config.get("storage")
    if not isinstance(storage, dict):
        raise ValueError("Config file must define a 'storage' mapping.")

    sqlite_path = storage.get("sqlite_path")
    if not isinstance(sqlite_path, str) or not sqlite_path:
        raise ValueError(
            "Config storage must define a non-empty 'sqlite_path' string."
        )

    notification = raw_config.get("notification")
    if not isinstance(notification, dict):
        raise ValueError("Config file must define a 'notification' mapping.")

    notification_type = notification.get("type")
    if not isinstance(notification_type, str) or not notification_type:
        raise ValueError(
            "Config notification must define a non-empty 'type' string."
        )

    bot_token_env = notification.get("bot_token_env")
    if bot_token_env is not None and not isinstance(bot_token_env, str):
        raise ValueError(
            "Config notification 'bot_token_env' must be a string if provided."
        )

    chat_id_env = notification.get("chat_id_env")
    if chat_id_env is not None and not isinstance(chat_id_env, str):
        raise ValueError(
            "Config notification 'chat_id_env' must be a string if provided."
        )

    matching = raw_config.get("matching")
    matching_config = _parse_matching_config(matching)

    polling = raw_config.get("polling")
    polling_config = _parse_polling_config(polling)

    return AppConfig(
        source=SourceConfig(
            type=source_type,
            url=source_url,
        ),
        storage=StorageConfig(
            sqlite_path=_resolve_config_path(path=Path(sqlite_path), config_path=path),
        ),
        notification=NotificationConfig(
            type=notification_type,
            bot_token_env=bot_token_env,
            chat_id_env=chat_id_env,
        ),
        matching=matching_config,
        polling=polling_config,
    )


def _parse_matching_config(raw_matching: object) -> MatchingConfig:
    """Parse optional item matching config.

    Args:
        raw_matching: Raw matching config loaded from YAML.

    Returns:
        Parsed matching config.

    Raises:
        ValueError: If matching config has an invalid shape.
    """
    if raw_matching is None:
        return MatchingConfig()

    if not isinstance(raw_matching, dict):
        raise ValueError("Config 'matching' must be a mapping if provided.")

    brands = raw_matching.get("brands", [])
    if brands is None:
        return MatchingConfig()

    if not isinstance(brands, list):
        raise ValueError("Config matching 'brands' must be a list if provided.")

    parsed_brands: list[str] = []
    for brand in brands:
        if not isinstance(brand, str) or not brand:
            raise ValueError(
                "Config matching 'brands' must contain non-empty strings."
            )
        parsed_brands.append(brand)

    return MatchingConfig(brands=tuple(parsed_brands))


def _parse_polling_config(raw_polling: object) -> PollingConfig:
    """Parse optional polling config.

    Args:
        raw_polling: Raw polling config loaded from YAML.

    Returns:
        Parsed polling config.

    Raises:
        ValueError: If polling config has an invalid shape.
    """
    if raw_polling is None:
        return PollingConfig()

    if not isinstance(raw_polling, dict):
        raise ValueError("Config 'polling' must be a mapping if provided.")

    interval_seconds = _parse_positive_int(
        value=raw_polling.get("interval_seconds", 3600),
        config_key="polling 'interval_seconds'",
    )
    jitter_seconds = _parse_non_negative_int(
        value=raw_polling.get("jitter_seconds", 600),
        config_key="polling 'jitter_seconds'",
    )

    return PollingConfig(
        interval_seconds=interval_seconds,
        jitter_seconds=jitter_seconds,
    )


def _parse_positive_int(value: object, config_key: str) -> int:
    """Parse a positive integer config value.

    Args:
        value: Raw config value.
        config_key: Config key used in error messages.

    Returns:
        Parsed positive integer.

    Raises:
        ValueError: If the value is not a positive integer.
    """
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"Config {config_key} must be a positive integer.")

    return value


def _parse_non_negative_int(value: object, config_key: str) -> int:
    """Parse a non-negative integer config value.

    Args:
        value: Raw config value.
        config_key: Config key used in error messages.

    Returns:
        Parsed non-negative integer.

    Raises:
        ValueError: If the value is not a non-negative integer.
    """
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"Config {config_key} must be a non-negative integer.")

    return value


def _resolve_config_path(path: Path, config_path: Path) -> Path:
    """Resolve a path from config relative to the config file location.

    Args:
        path: Path loaded from config.
        config_path: Path to the YAML configuration file.

    Returns:
        Absolute paths unchanged, relative paths resolved against the config
        file's parent directory.
    """
    if path.is_absolute():
        return path

    return (config_path.resolve().parent / path).resolve()
