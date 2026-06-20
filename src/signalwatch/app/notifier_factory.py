"""Create notifier instances from application config."""

from __future__ import annotations

from signalwatch.config import NotificationConfig
from signalwatch.notify.base import Notifier
from signalwatch.notify.log import LogNotifier


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

    raise ValueError(f"Unsupported notification type: {notification_config.type}")
