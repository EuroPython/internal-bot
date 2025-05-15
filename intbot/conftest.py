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


@pytest.fixture(scope="session")
def pretix_data():
    """Pytest fixture with examples of data from pretix"""
    base_path = settings.BASE_DIR / "tests" / "test_integrations" / "pretix"

    with open(base_path / "orders.json") as fd:
        orders = json.load(fd)

    with open(base_path / "products.json") as fd:
        products = json.load(fd)

    with open(base_path / "vouchers.json") as fd:
        vouchers = json.load(fd)

    return {
        "products": products,
        "orders": orders,
        "vouchers": vouchers,
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
