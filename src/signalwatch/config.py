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
class AppConfig:
    """Application configuration loaded from YAML."""

    source: SourceConfig
    storage: StorageConfig
    notification: NotificationConfig


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
    )


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
