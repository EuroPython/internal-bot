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
from pathlib import Path

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
        "DIRS": [],
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

    # This is only needed if you end up running the bot locally, hence it
    # doesn't fail explicilty – however it does emit a warning.
    # Please check the documentation and/or current online guides how to get
    # one from the developer portal.
    # If you run it locally, you probably want to run it against your own test
    # bot and a test server.

    def warn_if_missing(name, default=""):
        value = os.environ.get(name, default)
        if not value:
            warnings.warn(f"{name} not set")

    DISCORD_TEST_CHANNEL_ID = warn_if_missing("DISCORD_TEST_CHANNEL_ID", "")
    DISCORD_TEST_CHANNEL_NAME = warn_if_missing("DISCORD_TEST_CHANNEL_NAME", "")
    DISCORD_BOT_TOKEN = warn_if_missing("DISCORD_BOT_TOKEN", "")


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

    DISCORD_TEST_CHANNEL_ID = "12345"
    DISCORD_TEST_CHANNEL_NAME = "#test-channel"


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

    DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
    DISCORD_TEST_CHANNEL_ID = os.environ["DISCORD_TEST_CHANNEL_ID"]
    DISCORD_TEST_CHANNEL_NAME = os.environ["DISCORD_TEST_CHANNEL_NAME"]

    CSRF_TRUSTED_ORIGINS = [
        "https://internal.europython.eu",
    ]

    WEBHOOK_INTERNAL_TOKEN = os.environ["WEBHOOK_INTERNAL_TOKEN"]


elif DJANGO_ENV == "build":
    # Currently used only for collecting staticfiles in docker
    DEBUG = False

else:
    raise ValueError(f"Unsupported DJANGO_ENV `{DJANGO_ENV}`")
