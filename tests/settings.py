SECRET_KEY = "test-secret-key-not-for-production"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
USE_TZ = True
