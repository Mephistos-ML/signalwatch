"""Create notifier instances from application config."""

from __future__ import annotations

import os

from signalwatch.config import NotificationConfig
from signalwatch.notify.base import Notifier
from signalwatch.notify.log import LogNotifier
from signalwatch.notify.telegram import TelegramNotifier


def create_notifier(notification_config: NotificationConfig) -> Notifier:
    """Create a notifier from notification configuration.

    Args:
        notification_config: Notification configuration loaded from YAML.

    Returns:
        Configured notifier instance.

    Raises:
        ValueError: If the notification type is unsupported.
    """
    if notification_config.type == "log":
        return LogNotifier()

    if notification_config.type == "telegram":
        return _create_telegram_notifier(notification_config)

    raise ValueError(f"Unsupported notification type: {notification_config.type}")


def _create_telegram_notifier(
    notification_config: NotificationConfig,
) -> TelegramNotifier:
    """Create a Telegram notifier from notification configuration.

    Args:
        notification_config: Telegram notification configuration.

    Returns:
        Configured Telegram notifier instance.
    """
    return TelegramNotifier(
        bot_token=_read_telegram_env_value(
            env_name=notification_config.bot_token_env,
            config_key="bot_token_env",
        ),
        chat_id=_read_telegram_env_value(
            env_name=notification_config.chat_id_env,
            config_key="chat_id_env",
        ),
    )


def _read_telegram_env_value(env_name: str | None, config_key: str) -> str:
    """Read a required Telegram secret from the environment.

    Args:
        env_name: Environment variable name from config.
        config_key: Config key used in error messages.

    Returns:
        Environment variable value.

    Raises:
        ValueError: If the config key or environment variable is missing.
    """
    if env_name is None or not env_name:
        raise ValueError(
            f"Telegram notification requires a non-empty '{config_key}' value."
        )

    value = os.environ.get(env_name)
    if value is None or not value:
        raise ValueError(f"Environment variable '{env_name}' must be set.")

    return value
