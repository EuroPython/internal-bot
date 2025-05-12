import contextlib
import json
from unittest import mock

import pytest
from core.models import PretixData
from django.conf import settings
from django.db import connections


@pytest.fixture(scope="session")
def github_data():
    """Pytest fixture with examples of webhooks from github"""
    base_path = settings.BASE_DIR / "tests" / "test_integrations" / "github"

    return {
        "project_v2_item.edited": json.load(
            open(base_path / "project_v2_item.edited.json"),
        ),
        "query_result": json.load(
            open(base_path / "query_result.json"),
        )["data"]["node"],
    }


# NOTE(artcz)
# The fixture below (fix_async_db) is copied from this issue
# https://github.com/pytest-dev/pytest-asyncio/issues/226
# it seems to fix the issue and also speed up the test from ~6s down to 1s.
# Thanks to (@gbdlin) for help with debugging.


@pytest.fixture(autouse=True)
def fix_async_db(request):
    """

    If you don't use this fixture for async tests that use the ORM/database
    you won't get proper teardown of the database.
    This is a bug somehwere in pytest-django, pytest-asyncio or django itself.

    Nobody knows how to solve it, or who should solve it.
    Workaround here: https://github.com/django/channels/issues/1091#issuecomment-701361358
    More info:
    https://github.com/pytest-dev/pytest-django/issues/580
    https://code.djangoproject.com/ticket/32409
    https://github.com/pytest-dev/pytest-asyncio/issues/226


    The actual implementation of this workaround constists on ensuring
    Django always returns the same database connection independently of the thread
    the code that requests a db connection is in.

    We were unable to use better patching methods (the target is asgiref/local.py),
    so we resorted to mocking the _lock_storage context manager so that it returns a Mock.
    That mock contains the default connection of the main thread (instead of the connection
    of the running thread).

    This only works because our tests only ever use the default connection, which is the only thing our mock returns.

    We apologize in advance for the shitty implementation.
    """
    if (
        request.node.get_closest_marker("asyncio") is None
        or request.node.get_closest_marker("django_db") is None
    ):
        # Only run for async tests that use the database
        yield
        return

    main_thread_local = connections._connections
    for conn in connections.all():
        conn.inc_thread_sharing()

    main_thread_default_conn = main_thread_local._storage.default
    main_thread_storage = main_thread_local._lock_storage

    @contextlib.contextmanager
    def _lock_storage():
        yield mock.Mock(default=main_thread_default_conn)

    try:
        with mock.patch.object(main_thread_default_conn, "close"):
            object.__setattr__(main_thread_local, "_lock_storage", _lock_storage)
            yield
    finally:
        object.__setattr__(main_thread_local, "_lock_storage", main_thread_storage)


@pytest.fixture
def products_pretix_data():
    PretixData.objects.create(
        resource=PretixData.PretixResources.products,
        content=[
            {
                "id": 100,
                "category": 2000,
                "name": {"en": "Business"},
                "description": {
                    "en": "If your company pays for you to attend, or if you use Python professionally. When you purchase a Business Ticket, you help us keep the conference affordable for everyone. \r\nThank you!"
                },
                "default_price": "500.00",
                "admission": True,
                "variations": [
                    {
                        "id": 1,
                        "value": {"en": "Conference"},
                        "active": True,
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July). Tutorials (14-15 July) are **NOT** included. To access Tutorial days please buy a Tutorial or Combined ticket.\r\n\r\n**Net price \u20ac500.00 + 21% Czech VAT**.  \r\n\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "605.00",
                        "price": "605.00",
                    },
                    {
                        "id": 2,
                        "value": {"en": "Tutorials"},
                        "active": True,
                        "description": {
                            "en": "Access to Workshop/Tutorial Days (14-15 July) and the Sprint Weekend (19-20 July), but **NOT** the main conference (16-18 July). \r\n**Net price \u20ac400.00+ 21% Czech VAT.**\r\n\r\nTutorial tickets are only available until 27 June"
                        },
                        "default_price": "484.00",
                        "price": "484.00",
                    },
                    {
                        "id": 3,
                        "value": {"en": "Combined (Conference + Tutorials)"},
                        "active": True,
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n**Net price \u20ac800.00 + 21% Czech VAT.**\r\n\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "968.00",
                        "price": "968.00",
                    },
                    {
                        "id": 4,
                        "value": {"en": "Late Conference"},
                        "active": True,
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July) & limited access to specific sponsored/special workshops during the Workshop/Tutorial Days (14-15 July).\r\n**Net price \u20ac750.00 + 21% Czech VAT**\r\n\r\nAvailable from 27 June or after regular Conference tickets are sold out."
                        },
                        "default_price": "907.50",
                        "price": "907.50",
                    },
                    {
                        "id": 5,
                        "value": {"en": "Late Combined"},
                        "active": True,
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n**Net price \u20ac1,200.00 + 21% Czech VAT.**\r\n\r\nAvailable from 27 June or after regular Combined tickets are sold out."
                        },
                        "default_price": "1452.00",
                        "price": "1452.00",
                    },
                ],
            },
            {
                "id": 200,
                "category": 2000,
                "name": {"en": "Personal"},
                "active": True,
                "description": {
                    "en": "If you enjoy Python as a hobbyist or use it as a freelancer."
                },
                "default_price": "300.00",
                "variations": [
                    {
                        "id": 6,
                        "value": {"en": "Conference"},
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July). Tutorials (14-15 July) are **NOT** included. \r\nTo access Tutorial days please buy a Tutorial or Combined ticket.\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "300.00",
                        "price": "300.00",
                    },
                    {
                        "id": 7,
                        "value": {"en": "Tutorials"},
                        "description": {
                            "en": "Access to Workshop/Tutorial Days (14-15 July) and the Sprint Weekend (19-20 July), but **NOT** the main conference (16-18 July).\r\n\r\nAvailable until sold out or 27 June."
                        },
                        "default_price": "200.00",
                        "price": "200.00",
                    },
                    {
                        "id": 8,
                        "value": {"en": "Combined (Conference + Tutorials)"},
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n\r\nAvailable until sold out or 27 June."
                        },
                        "position": 2,
                        "default_price": "450.00",
                        "price": "450.00",
                    },
                    {
                        "id": 9,
                        "value": {"en": "Late Conference"},
                        "description": {
                            "en": "Access to Conference Days & Sprint Weekend (16-20 July). Tutorials (14-15 July) are NOT included. To access Tutorial days please buy a Tutorial or Combined ticket.\r\n\r\nAvailable from 27 June or after regular Conference tickets are sold out."
                        },
                        "default_price": "450.00",
                        "price": "450.00",
                    },
                    {
                        "id": 10,
                        "value": {"en": "Late Combined"},
                        "description": {
                            "en": "Access to everything during the whole seven-day event (14-20 July).\r\n\r\nAvailable from 27 June or after regular Combined tickets are sold out."
                        },
                        "default_price": "675.00",
                        "price": "675.00",
                    },
                ],
            },
        ],
    )
