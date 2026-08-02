# uploadkit-django

[![CI](https://github.com/uploadkit/uploadkit-django/actions/workflows/ci.yml/badge.svg)](https://github.com/uploadkit/uploadkit-django/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/uploadkit/uploadkit-django/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Django](https://img.shields.io/badge/django-4.2%2B-green)](pyproject.toml)

Django integration for UploadKit.

## What problem does this solve?

Adapts Django uploaded files and maps UploadKit exceptions to HTTP responses — without reimplementing validation or storage.

## When to use it

Use when your Django (or DRF) app uploads files through UploadKit Core.

## When not to use it

Do not put validators, policies, or storage implementations in this package.

## Installation

Requires **Python 3.10–3.13** and **Django 4.2+**.

```bash
pip install uploadkit-django
# optional security validators
pip install uploadkit-security
```

### Python × Django support

| Python | Django |
|--------|--------|
| 3.10–3.12 | Django 4.2+ |
| 3.13 | Newest Django that declares support for 3.13 (verified in CI) |

Python 3.14 will be added once Django officially supports it.

## Quick Start

```python
from django.http import JsonResponse
from uploadkit import Uploader, UploadPolicy
from uploadkit_django import as_uploadable, json_error_response
from uploadkit_security import default_validators
from uploadkit import UploaderError

def upload_view(request):
    storage = ...  # your StorageProvider
    policy = UploadPolicy(
        max_size=5 * 1024 * 1024,
        allowed_extensions=frozenset({"png"}),
        allowed_mime_types=frozenset({"image/png"}),
        validators=default_validators(),
    )
    try:
        result = Uploader(policy, storage).upload(
            as_uploadable(request.FILES["file"]),
            bucket="uploads",
            object_name="path/file.png",
        )
    except UploaderError as exc:
        return json_error_response(exc)
    return JsonResponse({"object_name": result.object_name, "sha256": result.sha256})
```

### Settings

```python
# settings.py
UPLOADKIT_STORAGE_PROVIDER = "myapp.storage.get_provider"  # callable factory
```

```python
from uploadkit_django import get_storage_provider
storage = get_storage_provider()
```

## Architecture

Thin adapters over UploadKit Core protocols. Django's `UploadedFile` already satisfies `UploadableFile`; `as_uploadable` makes that explicit.

## Public API

| Symbol | Kind |
|--------|------|
| `as_uploadable` | Public |
| `json_error_response` / `status_for_error` / `error_payload` | Public |
| `get_storage_provider` | Public |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
