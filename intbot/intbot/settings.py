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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    "django_extensions",
    # Project apps
    "core",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise to serve static files
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'intbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'intbot.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / ".." / "_static_root"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_ENV = os.environ["DJANGO_ENV"]

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

    WEBHOOK_INTERNAL_TOKEN = "dev-token"

    # This is only needed if you end up running the bot locally, hence it
    # doesn't fail explicilty – however it does emit a warning.
    # Please check the documentation and/or current online guides how to get
    # one from the developer portal.
    # If you run it locally, you probably want to run it against your own test
    # bot and a test server.
    DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
    if not DISCORD_BOT_TOKEN:
        warnings.warn("DISCORD_BOT_TOKEN not set")

elif DJANGO_ENV == "test":
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

    WEBHOOK_INTERNAL_TOKEN = "test-random-token"


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




elif DJANGO_ENV == "build":
    # Currently used only for collecting staticfiles in docker
    DEBUG = False

else:
    raise ValueError(f"Unsupported DJANGO_ENV `{DJANGO_ENV}`")
