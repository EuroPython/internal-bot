from unittest.mock import AsyncMock, patch

import discord
import pytest
from core.bot.main import (
    INBOX_EMOJI,
    inbox,
    on_raw_reaction_add,
    on_raw_reaction_remove,
)
from core.models import InboxItem
from django.utils import timezone



@pytest.mark.asyncio
@pytest.mark.django_db
async def test_inbox_command_with_empty_inbox():
    """Test the inbox command when the user has no items in their inbox."""
    # Mock context
    ctx = AsyncMock()
    ctx.message.author.id = "12345"

    # Call the command
    await inbox(ctx)

    # Assert that the command sent the expected message for empty inbox
    ctx.send.assert_called_once_with("Your inbox is empty.")


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_inbox_command_with_items():
    """Test the inbox command when the user has items in their inbox."""
    # Mock context
    ctx = AsyncMock()
    ctx.message.author.id = "12345"

    # Create test inbox items for this user
    await InboxItem.objects.acreate(
        message_id="111111",
        channel_id="222222",
        channel_name="#test-channel",
        server_id="333333",
        user_id="12345",
        author="Test User",
        content="Test message 1",
    )

    await InboxItem.objects.acreate(
        message_id="444444",
        channel_id="222222",
        channel_name="#test-channel",
        server_id="333333",
        user_id="12345",
        author="Another User",
        content="Test message 2",
    )

    # Call the command
    await inbox(ctx)

    # Assert that the command sent an embed with item summaries
    ctx.send.assert_called_once()
    # Get the embed argument
    args, kwargs = ctx.send.call_args
    embed = kwargs.get("embed") or args[0]

    # Check embed content contains summaries of both items
    assert isinstance(embed, discord.Embed)
    assert embed.description  # asserting here mostly for type checks below
    assert "Currently tracking the following messages:" in embed.description
    assert "Test User" in embed.description
    assert "Another User" in embed.description
    assert "Test message 1" in embed.description
    assert "Test message 2" in embed.description


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_on_raw_reaction_add_creates_inbox_item():
    """Test that reacting with the inbox emoji creates a new inbox item."""
    # Create mock payload
    payload = AsyncMock()
    payload.emoji.name = INBOX_EMOJI
    payload.channel_id = 222222
    payload.message_id = 111111
    payload.guild_id = 333333
    payload.user_id = 12345

    # Create mock channel and message
    mock_channel = AsyncMock()
    mock_channel.name = "test-channel"
    mock_message = AsyncMock()
    mock_message.id = 111111
    mock_message.author.name = "Test User"
    mock_message.content = "Test message content"

    # Mock bot.get_channel to return our mock channel
    with patch("core.bot.main.bot.get_channel", return_value=mock_channel):
        # Mock channel.fetch_message to return our mock message
        mock_channel.fetch_message.return_value = mock_message

        # Call the event handler
        await on_raw_reaction_add(payload)

    # Check that an inbox item was created with the correct data
    items = await InboxItem.objects.filter(
        message_id="111111", user_id="12345"
    ).acount()

    assert items == 1


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_on_raw_reaction_remove_deletes_inbox_item():
    """Test that removing the inbox emoji reaction deletes the inbox item."""
    # Create test inbox item
    await InboxItem.objects.acreate(
        message_id="111111",
        channel_id="222222",
        channel_name="#test-channel",
        server_id="333333",
        user_id="12345",
        author="Test User",
        content="Test message content",
    )

    # Create mock payload for the reaction remove event
    payload = AsyncMock()
    payload.emoji.name = INBOX_EMOJI
    payload.message_id = "111111"
    payload.user_id = "12345"

    # Call the event handler
    await on_raw_reaction_remove(payload)

    # Check that the inbox item was deleted
    items = await InboxItem.objects.filter(
        message_id="111111", user_id="12345"
    ).acount()

    assert items == 0


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_on_raw_reaction_remove_ignores_other_emojis():
    """Test that removing a non-inbox emoji doesn't delete the inbox item."""
    # Create test inbox item
    await InboxItem.objects.acreate(
        message_id="111111",
        channel_id="222222",
        channel_name="#test-channel",
        server_id="333333",
        user_id="12345",
        author="Test User",
        content="Test message content",
    )

    # Create mock payload for a different emoji reaction
    payload = AsyncMock()
    payload.emoji.name = "👍"  # Different emoji
    payload.message_id = "111111"
    payload.user_id = "12345"

    # Call the event handler
    await on_raw_reaction_remove(payload)

    # Check that the inbox item was not deleted
    items = await InboxItem.objects.filter(
        message_id="111111", user_id="12345"
    ).acount()

    assert items == 1


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_inboxitem_url_method():
    """Test the URL generation method of the InboxItem model."""
    item = InboxItem(
        message_id="111111",
        channel_id="222222",
        server_id="333333",
    )

    expected_url = "https://discord.com/channels/333333/222222/111111"
    assert item.url() == expected_url


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_inboxitem_summary_method():
    """Test the summary method of the InboxItem model."""
    # Create an InboxItem with a known created_at time
    fixed_time = timezone.now()
    timestamp_str = fixed_time.strftime("%Y-%m-%d %H:%M")

    item = InboxItem(
        message_id="111111",
        channel_id="222222",
        channel_name="#test-channel",
        server_id="333333",
        author="Test User",
        content="This is a test message with more than 30 characters",
        created_at=fixed_time,
    )

    # Generate the expected summary
    expected_summary = f"`{timestamp_str}` | from **Test User** @ **#test-channel**: [This is a test message with mo...](https://discord.com/channels/333333/222222/111111)"

    # Get the actual summary and compare
    summary = item.summary()
    assert expected_summary == summary
