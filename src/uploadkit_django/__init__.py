"""Django integration for UploadKit.

Owns request adapters, response helpers, and Django configuration only.
Does not implement validators, policies, or storage.
"""

from uploadkit_django.adapters import as_uploadable
from uploadkit_django.conf import ImproperlyConfiguredUploadKit, get_storage_provider
from uploadkit_django.responses import (
    ERROR_STATUS,
    error_payload,
    json_error_response,
    status_for_error,
)

__all__ = [
    "as_uploadable",
    "get_storage_provider",
    "ImproperlyConfiguredUploadKit",
    "ERROR_STATUS",
    "status_for_error",
    "error_payload",
    "json_error_response",
]

__version__ = "0.1.1"
