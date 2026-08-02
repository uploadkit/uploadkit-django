"""Adapt Django uploaded files for UploadKit Core."""

from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile

from uploadkit import UploadableFile


def as_uploadable(file: UploadedFile) -> UploadableFile:
    """Return ``file`` as an ``UploadableFile``.

    Django's ``UploadedFile`` already duck-types the Core protocol
    (``name``, ``size``, ``content_type``, ``read`` / ``seek`` / ``tell``).
    This helper makes the adapter explicit at call sites.
    """
    return file  # type: ignore[return-value]
