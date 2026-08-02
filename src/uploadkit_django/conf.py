"""Django settings helpers for UploadKit."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.conf import settings

from uploadkit import StorageProvider


def get_storage_provider() -> StorageProvider:
    """Resolve ``UPLOADKIT_STORAGE_PROVIDER`` from Django settings.

    The setting must be a callable that returns a ``StorageProvider``,
    or a dotted path string to such a callable.
    """
    value: Any = getattr(settings, "UPLOADKIT_STORAGE_PROVIDER", None)
    if value is None:
        raise ImproperlyConfiguredUploadKit(
            "Set UPLOADKIT_STORAGE_PROVIDER to a StorageProvider factory"
        )
    if isinstance(value, str):
        from django.utils.module_loading import import_string

        value = import_string(value)
    if not callable(value):
        raise ImproperlyConfiguredUploadKit(
            "UPLOADKIT_STORAGE_PROVIDER must be a callable factory"
        )
    provider = value()
    return provider


class ImproperlyConfiguredUploadKit(Exception):
    """Raised when Django UploadKit settings are missing or invalid."""


StorageFactory = Callable[[], StorageProvider]
