from unittest.mock import AsyncMock, patch

import discord
import polars as pl
import pytest
from asgiref.sync import sync_to_async
from core.bot.main import (
    close,
    ping,
    poll_database,
    qlen,
    source,
    submissions_status,
    submissions_status_pie_chart,
    until,
    version,
    wiki,
)
from core.models import DiscordMessage, PretalxData
from django.utils import timezone
from freezegun import freeze_time


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
async def test_close_command_working():
    # Mock context
    ctx = AsyncMock()
    ctx.channel = AsyncMock()
    ctx.message.author = AsyncMock()
    ctx.channel.type = discord.ChannelType.public_thread

    # Call the command
    await close(ctx)

    # Assert that the command sent the expected message
    ctx.channel.send.assert_called_once_with(
        f"# This was marked as done by {ctx.message.author.mention}",
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_close_command_notworking():
    # Mock context
    ctx = AsyncMock()
    ctx.channel = AsyncMock()

    # Call the command
    await close(ctx)

    # Assert that the command sent the expected message
    ctx.channel.send.assert_called_once_with(
        "The !close command is intended to be used inside a thread/post",
        suppress_embeds=True,
        delete_after=5,
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


@pytest.mark.asyncio
@freeze_time("2025-04-05")
async def test_until():
    ctx = AsyncMock()

    await until(ctx)

    ctx.send.assert_called_once_with("100 days left until the conference")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_submissions_status():
    ctx = AsyncMock()
    await PretalxData.objects.acreate(
        resource=PretalxData.PretalxResources.submissions,
        content=[
            {
                "code": "ABCDEF",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "",
                "state": "submitted",
                "title": "Title",
                "track": {"en": "Machine Learning, NLP and CV"},
                "created": "2025-01-14T01:24:36.328974+01:00",
                "answers": [],
                "tag_ids": [],
                "abstract": "Abstract",
                "duration": 30,
                "speakers": [],
                "submission_type": "Talk",
            },
            {
                "code": "DEFGHI",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "",
                "state": "submitted",
                "title": "Title",
                "track": {"en": "Machine Learning, NLP and CV"},
                "created": "2025-01-14T01:24:36.328974+01:00",
                "answers": [],
                "tag_ids": [],
                "abstract": "Abstract",
                "duration": 30,
                "speakers": [],
                "submission_type": "Talk",
            },
            {
                "code": "XYZF12",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "Notes",
                "state": "withdrawn",
                "title": "Title 2",
                "track": {"en": "Track 2"},
                "answers": [],
                "created": "2025-01-16T11:44:26.328974+01:00",
                "tag_ids": [],
                "abstract": "Minimal Abstract",
                "duration": 45,
                "speakers": [],
                "submission_type": {"en": "Talk (long session)"},
            },
        ],
    )
    # Sorted from bigger to smaller
    expected = pl.DataFrame({"state": ["submitted", "withdrawn"], "len": [2, 1]})
    expected = expected.cast({"len": pl.UInt32})  # need cast to make it consistent

    await submissions_status(ctx)

    ctx.send.assert_called_once_with(f"```{str(expected)}```")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_submissions_status_pie_chart():
    ctx = AsyncMock()
    await PretalxData.objects.acreate(
        resource=PretalxData.PretalxResources.submissions,
        content=[
            {
                "code": "ABCDEF",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "",
                "state": "submitted",
                "title": "Title",
                "track": {"en": "Machine Learning, NLP and CV"},
                "created": "2025-01-14T01:24:36.328974+01:00",
                "answers": [],
                "tag_ids": [],
                "abstract": "Abstract",
                "duration": 30,
                "speakers": [],
                "submission_type": "Talk",
            },
            {
                "code": "XYZF12",
                "slot": None,
                "tags": [],
                "image": None,
                "notes": "Notes",
                "state": "withdrawn",
                "title": "Title 2",
                "track": {"en": "Track 2"},
                "answers": [],
                "created": "2025-01-16T11:44:26.328974+01:00",
                "tag_ids": [],
                "abstract": "Minimal Abstract",
                "duration": 45,
                "speakers": [],
                "submission_type": {"en": "Talk (long session)"},
            },
        ],
    )

    class FakeFig:
        def to_image(self, *, format):
            return b"PNG GOES HERE"

    expected = FakeFig()

    with patch("core.bot.main.piechart_submissions_by_state", return_value=expected):
        await submissions_status_pie_chart(ctx)

    ctx.send.assert_called_once()
    sent_file = ctx.send.call_args.kwargs["file"]

    assert isinstance(sent_file, discord.File)
    assert sent_file.filename == "submissions_by_state.png"
    sent_file.fp.seek(0)
    assert sent_file.fp.read() == b"PNG GOES HERE"
