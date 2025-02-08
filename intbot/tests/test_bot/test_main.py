from unittest import mock
from unittest.mock import AsyncMock, patch
import contextlib
import discord

from django.db import connections

import pytest
from asgiref.sync import sync_to_async
from core.bot.main import ping, poll_database, qlen, source, version, wiki, close
from core.models import DiscordMessage
from django.utils import timezone

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
        with patch.object(main_thread_default_conn, "close"):
            object.__setattr__(main_thread_local, "_lock_storage", _lock_storage)
            yield
    finally:
        object.__setattr__(main_thread_local, "_lock_storage", main_thread_storage)


@pytest.mark.asyncio
async def test_ping_command():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await ping(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("Pong!")


@pytest.mark.asyncio
async def test_wiki_command():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await wiki(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with(
        "Please add it to the wiki: "
        "[ep2025-wiki.europython.eu](https://ep2025-wiki.europython.eu)",
        suppress_embeds=True,
    )

@pytest.mark.asyncio
async def test_close_command():
    # Mock context
    ctx = AsyncMock()
    ctx.channel = discord.Thread()
    ctx.channel.parent = discord.ForumChannel()
    ctx.author = discord.Member()
    ctx.author.mention = "TestUser"

    # Call the command
    await close(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with(
        "# This was marked as done by {ctx.author.mention}",
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_version_command():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await version(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("Version: latest")


@pytest.mark.asyncio
async def test_source_command():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await source(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with(
        "I'm here: https://github.com/europython/internal-bot",
        suppress_embeds=True,
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_qlen_command_returns_zero_if_no_messages():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await qlen(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("In the queue there are: 0 messages")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_qlen_command_returns_zero_if_all_messages_sent():
    # Mock context
    ctx = AsyncMock()
    await DiscordMessage.objects.acreate(sent_at=timezone.now())

    # Call the command
    await qlen(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("In the queue there are: 0 messages")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_qlen_command_correctly_counts_unsent_messags():
    # Mock context
    ctx = AsyncMock()
    for _ in range(3):
        await DiscordMessage.objects.acreate(
            channel_id="1234",
            content="foobar",
            sent_at=None,
        )

    # Call the command
    await qlen(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("In the queue there are: 3 messages")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_polling_messages_sends_nothing_without_messages():
    mock_channel = AsyncMock()
    mock_channel.send = AsyncMock()

    with patch("core.bot.main.bot.get_channel", return_value=mock_channel):
        await poll_database()

    mock_channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_polling_messages_sends_nothing_if_all_messages_are_sent():
    mock_channel = AsyncMock()
    mock_channel.send = AsyncMock()
    await DiscordMessage.objects.acreate(sent_at=timezone.now())

    with patch("core.bot.main.bot.get_channel", return_value=mock_channel):
        await poll_database()

    mock_channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_polling_messages_sends_message_if_not_sent_and_sets_sent_at():
    start = timezone.now()
    dm = await DiscordMessage.objects.acreate(
        channel_id="1234",
        content="asdf",
        sent_at=None,
    )
    mock_channel = AsyncMock()
    mock_channel.send = AsyncMock()

    with patch("core.bot.main.bot.get_channel", return_value=mock_channel):
        await poll_database()

    mock_channel.send.assert_called_once_with("asdf", suppress_embeds=True)
    await sync_to_async(dm.refresh_from_db)()
    assert dm.sent_at is not None
    end = timezone.now()
    assert start < dm.sent_at < end
