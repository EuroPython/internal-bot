"""
Django settings for intbot project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "django_extensions",
    "django_tasks",
    "django_tasks.backends.database",
    # Project apps
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Whitenoise to serve static files
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "intbot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "intbot.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / ".." / "_static_root"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DJANGO_ENV = os.environ["DJANGO_ENV"]
APP_VERSION = os.environ.get("APP_VERSION", "latest")[:8]

# Just to make mypy happy
TASKS: dict[str, Any]


CONFERENCE_START = datetime(2025, 7, 14, tzinfo=timezone.utc)


# There are bunch of settings that we can skip on dev/testing environments if
# not used - that should be always present on prod/staging deployments.
# Instead of repeating them per-env below, they go here.
def get(name) -> str:
    value = os.environ.get(name)

    if DJANGO_ENV == "prod":
        if value is None:
            raise ValueError(f"{name} is not set")

    elif DJANGO_ENV == "test":
        # For tests we hardcode below, and if something is missing the tests
        # will fail.
        pass
    else:
        warnings.warn(f"{name} not set")

    return value or ""


# Discord
# This is only needed if you end up running the bot locally, hence it
# doesn't fail explicilty – however it does emit a warning.
# Please check the documentation and/or current online guides how to get
# one from the developer portal.
# If you run it locally, you probably want to run it against your own test
# bot and a test server.
DISCORD_BOT_TOKEN = get("DISCORD_BOT_TOKEN")

DISCORD_TEST_CHANNEL_ID = get("DISCORD_TEST_CHANNEL_ID")
DISCORD_TEST_CHANNEL_NAME = get("DISCORD_TEST_CHANNEL_NAME")
DISCORD_BOARD_CHANNEL_ID = get("DISCORD_BOARD_CHANNEL_ID")
DISCORD_BOARD_CHANNEL_NAME = get("DISCORD_BOARD_CHANNEL_NAME")
DISCORD_EP2025_CHANNEL_ID = get("DISCORD_EP2025_CHANNEL_ID")
DISCORD_EP2025_CHANNEL_NAME = get("DISCORD_EP2025_CHANNEL_NAME")
DISCORD_EM_CHANNEL_ID = get("DISCORD_EM_CHANNEL_ID")
DISCORD_EM_CHANNEL_NAME = get("DISCORD_EM_CHANNEL_NAME")
DISCORD_WEBSITE_CHANNEL_ID = get("DISCORD_WEBSITE_CHANNEL_ID")
DISCORD_WEBSITE_CHANNEL_NAME = get("DISCORD_WEBSITE_CHANNEL_NAME")
DISCORD_BOT_CHANNEL_ID = get("DISCORD_BOT_CHANNEL_ID")
DISCORD_BOT_CHANNEL_NAME = get("DISCORD_BOT_CHANNEL_NAME")

DISCORD_HELPDESK_CHANNEL_ID = get("DISCORD_HELPDESK_CHANNEL_ID")
DISCORD_HELPDESK_CHANNEL_NAME = get("DISCORD_HELPDESK_CHANNEL_NAME")
DISCORD_BILLING_CHANNEL_ID = get("DISCORD_BILLING_CHANNEL_ID")
DISCORD_BILLING_CHANNEL_NAME = get("DISCORD_BILLING_CHANNEL_NAME")
DISCORD_PROGRAMME_CHANNEL_ID = get("DISCORD_PROGRAMME_CHANNEL_ID")
DISCORD_PROGRAMME_CHANNEL_NAME = get("DISCORD_PROGRAMME_CHANNEL_NAME")
DISCORD_FINAID_CHANNEL_ID = get("DISCORD_FINAID_CHANNEL_ID")
DISCORD_FINAID_CHANNEL_NAME = get("DISCORD_FINAID_CHANNEL_NAME")
DISCORD_SPONSORS_CHANNEL_ID = get("DISCORD_SPONSORS_CHANNEL_ID")
DISCORD_SPONSORS_CHANNEL_NAME = get("DISCORD_SPONSORS_CHANNEL_NAME")
DISCORD_GRANTS_CHANNEL_ID = get("DISCORD_GRANTS_CHANNEL_ID")
DISCORD_GRANTS_CHANNEL_NAME = get("DISCORD_GRANTS_CHANNEL_NAME")

DISCORD_STANDUP_CHANNEL_ID = get("DISCORD_STANDUP_CHANNEL_ID")
DISCORD_STANDUP_CHANNEL_NAME = get("DISCORD_STANDUP_CHANNEL_NAME")

# Discord Roles
DISCORD_BOARD_MEMBER_ROLE_ID = get("DISCORD_BOARD_MEMBER_ROLE_ID")

# Github
GITHUB_API_TOKEN = get("GITHUB_API_TOKEN")
GITHUB_WEBHOOK_SECRET_TOKEN = get("GITHUB_WEBHOOK_SECRET_TOKEN")

GITHUB_BOARD_PROJECT_ID = get("GITHUB_BOARD_PROJECT_ID")
GITHUB_EP2025_PROJECT_ID = get("GITHUB_EP2025_PROJECT_ID")
GITHUB_EM_PROJECT_ID = get("GITHUB_EM_PROJECT_ID")

# Zammad
ZAMMAD_WEBHOOK_SECRET_TOKEN = get("ZAMMAD_WEBHOOK_SECRET_TOKEN")

ZAMMAD_URL = "servicedesk.europython.eu"
ZAMMAD_GROUP_BILLING = get("ZAMMAD_GROUP_BILLING")
ZAMMAD_GROUP_HELPDESK = get("ZAMMAD_GROUP_HELPDESK")
ZAMMAD_GROUP_PROGRAMME = get("ZAMMAD_GROUP_PROGRAMME")
ZAMMAD_GROUP_FINAID = get("ZAMMAD_GROUP_FINAID")
ZAMMAD_GROUP_SPONSORS = get("ZAMMAD_GROUP_SPONSORS")
ZAMMAD_GROUP_GRANTS = get("ZAMMAD_GROUP_GRANTS")

# Pretalx
PRETALX_API_TOKEN = get("PRETALX_API_TOKEN")

# Pretix
PRETIX_API_TOKEN = get("PRETIX_API_TOKEN")


if DJANGO_ENV == "dev":
    DEBUG = True
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

    SECRET_KEY = "django-insecure-secret"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "intbot_database_dev",
            "USER": "intbot_user",
            "PASSWORD": "intbot_password",
            "HOST": "localhost",
            "PORT": "14672",
        }
    }

    TASKS = {
        "default": {
            "BACKEND": "django_tasks.backends.database.DatabaseBackend",
        }
    }

    WEBHOOK_INTERNAL_TOKEN = "dev-token"


elif DJANGO_ENV == "test":
    DEBUG = True
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

    SECRET_KEY = "django-insecure-secret"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "intbot_database_test",
            "USER": "intbot_user",
            "PASSWORD": "intbot_password",
            "HOST": "localhost",
            "PORT": "14672",
        }
    }

    WEBHOOK_INTERNAL_TOKEN = "test-random-token"

    TASKS = {
        "default": {
            "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
            # This setting doesn't really make sense in this context, but it
            # makes it work in the test environment...
            # TODO(artcz): Let's figure out later why.
            # NOTE: in django-tasks tests the test harness seem to be quite
            # different so maybe there's also something we can check in the
            # library itself.
            "ENQUEUE_ON_COMMIT": False,
        }
    }

    DISCORD_BOT_TOKEN = "test-token"
    DISCORD_TEST_CHANNEL_ID = "12345"
    DISCORD_TEST_CHANNEL_NAME = "#test-channel"
    GITHUB_API_TOKEN = "github-test-token"
    GITHUB_WEBHOOK_SECRET_TOKEN = "github-webhook-secret-token-token"

    # IRL those IDs are random and look like "id": "PVT_kwDOAFSD_s4AtxZm"
    GITHUB_BOARD_PROJECT_ID = "PVT_Test_Board_Project"
    GITHUB_EP2025_PROJECT_ID = "PVT_Test_ep2025_Project"
    GITHUB_EM_PROJECT_ID = "PVT_Test_EM_Project"

    DISCORD_BOARD_CHANNEL_NAME = "board_channel"
    DISCORD_BOARD_CHANNEL_ID = "1234567"
    DISCORD_EP2025_CHANNEL_NAME = "ep2025_channel"
    DISCORD_EP2025_CHANNEL_ID = "1232025"
    DISCORD_EM_CHANNEL_NAME = "em_channel"
    DISCORD_EM_CHANNEL_ID = "123123"

    DISCORD_HELPDESK_CHANNEL_ID = "1237777"
    DISCORD_HELPDESK_CHANNEL_NAME = "helpdesk_channel"
    DISCORD_BILLING_CHANNEL_ID = "123999"
    DISCORD_BILLING_CHANNEL_NAME = "billing_channel"

    ZAMMAD_GROUP_HELPDESK = "TestZammad Helpdesk"
    ZAMMAD_GROUP_BILLING = "TestZammad Billing"

    PRETALX_API_TOKEN = "Test-Pretalx-API-token"


elif DJANGO_ENV == "local_container":
    DEBUG = False
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

    SECRET_KEY = "django-insecure-secret"

    # Same postgres instance as local dev, but different config
    # We're going through the host network to connect to the postgres running
    # on the same exposed port as local dev
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "intbot_database_dev",
            "USER": "intbot_user",
            "PASSWORD": "intbot_password",
            "HOST": "host.internal",
            "PORT": "14672",
        }
    }

    TASKS = {
        "default": {
            "BACKEND": "django_tasks.backends.database.DatabaseBackend",
        }
    }

    # For 500 errors to appear on stderr
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": True,
            },
        },
    }


elif DJANGO_ENV == "prod":
    DEBUG = False
    SECRET_KEY = os.environ["SECRET_KEY"]

    ALLOWED_HOSTS = [
        "127.0.0.1",
        "localhost",
        "internal.europython.eu",
    ]

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
            "HOST": "db",
            "PORT": "5432",  # internal port
        }
    }

    TASKS = {
        "default": {
            "BACKEND": "django_tasks.backends.database.DatabaseBackend",
        }
    }

    # For 500 errors to appear on stderr
    # For now it's good for docker, in the future sentry/or rollabar should be
    # here
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": True,
            },
        },
    }

    CSRF_TRUSTED_ORIGINS = [
        "https://internal.europython.eu",
    ]


elif DJANGO_ENV == "build":
    # Currently used only for collecting staticfiles in docker
    DEBUG = False

elif DJANGO_ENV == "ci":
    DEBUG = False

else:
    raise ValueError(f"Unsupported DJANGO_ENV `{DJANGO_ENV}`")
