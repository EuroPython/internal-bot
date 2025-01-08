from unittest.mock import AsyncMock

import pytest
from core.bot.main import ping, version


@pytest.mark.asyncio
async def test_ping_command():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await ping(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("Pong!")


@pytest.mark.asyncio
async def test_version_command():
    # Mock context
    ctx = AsyncMock()

    # Call the command
    await version(ctx)

    # Assert that the command sent the expected message
    ctx.send.assert_called_once_with("Version: latest")
