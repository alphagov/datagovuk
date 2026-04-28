"""
With these settings, tests run faster.
"""

from .base import *  # noqa: F403
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="WkCdJu837wEcjaD3xmLuH8CNYP6bp0YM2ieks8FWd6d72Y4HsuS2pWfRy1vt9ZHz",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "http://media.testserver/"
# Your stuff...
# ------------------------------------------------------------------------------
GOOGLE_TAG_MANAGER_ID = env("GOOGLE_TAG_MANAGER_ID", default="UA-XXXXX-Y")
GOOGLE_TAG_MANAGER_AUTH = env("GOOGLE_TAG_MANAGER_AUTH", default="fake-auth-token")
GOOGLE_TAG_MANAGER_PREVIEW = env("GOOGLE_TAG_MANAGER_PREVIEW", default="fake-preview-token")
