from __future__ import annotations

import pytest
from django.core.files.uploadedfile import (
    InMemoryUploadedFile,
    SimpleUploadedFile,
    TemporaryUploadedFile,
)
from django.test import override_settings

from uploadkit import (
    EmptyFile,
    FileTooLarge,
    InvalidExtension,
    InvalidFileContent,
    InvalidFileName,
    InvalidMimeType,
    UploadFailed,
    UploadPolicy,
    Uploader,
    UploaderError,
)
from uploadkit_django import (
    ImproperlyConfiguredUploadKit,
    as_uploadable,
    error_payload,
    get_storage_provider,
    json_error_response,
    status_for_error,
)
from uploadkit_security import default_validators
from uploadkit_testing import FakeStorageProvider


def make_fake_storage() -> FakeStorageProvider:
    return FakeStorageProvider(etag="from-dotted-path")


def test_as_uploadable_round_trip() -> None:
    uploaded = SimpleUploadedFile("hello.txt", b"hello", content_type="text/plain")
    file = as_uploadable(uploaded)
    assert file.name == "hello.txt"
    assert file.read() == b"hello"


def test_as_uploadable_in_memory_uploaded_file() -> None:
    raw = SimpleUploadedFile("mem.txt", b"memory", content_type="text/plain")
    uploaded = InMemoryUploadedFile(
        file=raw.file,
        field_name="file",
        name="mem.txt",
        content_type="text/plain",
        size=6,
        charset=None,
    )
    file = as_uploadable(uploaded)
    assert file.name == "mem.txt"
    assert file.size == 6
    assert file.read() == b"memory"


def test_as_uploadable_temporary_uploaded_file() -> None:
    uploaded = TemporaryUploadedFile(
        name="tmp.txt",
        content_type="text/plain",
        size=4,
        charset=None,
    )
    try:
        uploaded.write(b"temp")
        uploaded.seek(0)
        file = as_uploadable(uploaded)
        assert file.name == "tmp.txt"
        assert file.read() == b"temp"
    finally:
        uploaded.close()


def test_upload_with_django_file() -> None:
    storage = FakeStorageProvider()
    policy = UploadPolicy(
        max_size=1024,
        allowed_extensions=frozenset({"txt"}),
        allowed_mime_types=frozenset({"text/plain"}),
        validators=default_validators(),
    )
    uploaded = SimpleUploadedFile("note.txt", b"hello world", content_type="text/plain")
    result = Uploader(policy, storage).upload(
        as_uploadable(uploaded),
        bucket="uploads",
        object_name="note.txt",
    )
    assert result.original_name == "note.txt"
    assert result.sha256 is not None
    assert len(storage.objects) == 1


@pytest.mark.parametrize(
    ("exc", "expected_status"),
    [
        (FileTooLarge("too big"), 413),
        (EmptyFile("empty"), 400),
        (InvalidExtension("bad ext"), 400),
        (InvalidMimeType("bad mime"), 400),
        (InvalidFileName("bad name"), 400),
        (InvalidFileContent("bad content"), 400),
        (UploadFailed("storage down"), 502),
        (UploaderError("generic"), 400),
    ],
)
def test_status_for_error_mapping(
    exc: UploaderError,
    expected_status: int,
) -> None:
    assert status_for_error(exc) == expected_status


def test_json_error_response() -> None:
    response = json_error_response(InvalidExtension("bad"))
    assert response.status_code == 400
    assert error_payload(InvalidExtension("bad"))["error"] == "InvalidExtension"


def test_json_error_response_file_too_large() -> None:
    response = json_error_response(FileTooLarge("too big"))
    assert response.status_code == 413
    assert error_payload(FileTooLarge("too big"))["error"] == "FileTooLarge"


def test_json_error_response_upload_failed() -> None:
    response = json_error_response(UploadFailed("down"))
    assert response.status_code == 502


def test_get_storage_provider_missing() -> None:
    with pytest.raises(ImproperlyConfiguredUploadKit):
        get_storage_provider()


@override_settings(UPLOADKIT_STORAGE_PROVIDER=lambda: FakeStorageProvider(etag="from-settings"))
def test_get_storage_provider_callable() -> None:
    provider = get_storage_provider()
    etag = provider.put(
        bucket="b",
        object_name="o",
        body=b"x",
        content_type="text/plain",
    )
    assert etag == "from-settings"


@override_settings(UPLOADKIT_STORAGE_PROVIDER="tests.test_django.make_fake_storage")
def test_get_storage_provider_dotted_path() -> None:
    provider = get_storage_provider()
    assert (
        provider.put(
            bucket="b",
            object_name="o",
            body=b"x",
            content_type="text/plain",
        )
        == "from-dotted-path"
    )


@override_settings(UPLOADKIT_STORAGE_PROVIDER="does.not.exist.factory")
def test_get_storage_provider_bad_dotted_path() -> None:
    with pytest.raises(ImportError):
        get_storage_provider()


@override_settings(UPLOADKIT_STORAGE_PROVIDER=123)
def test_get_storage_provider_non_callable() -> None:
    with pytest.raises(ImproperlyConfiguredUploadKit, match="callable"):
        get_storage_provider()
