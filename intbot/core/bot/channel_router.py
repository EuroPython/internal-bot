"""
Channel router that decides where to send particular message
"""

from dataclasses import dataclass
from core.models import Webhook

from core.integrations.github import GithubProjects, GithubRepositories
from core.integrations.github import GithubWebhook
from django.conf import settings

@dataclass
class DiscordChannel:
    channel_id: int
    channel_name: str



dont_send_it = DiscordChannel(channel_id=0, channel_name="/dev/null")

class Channels:
    test_channel = DiscordChannel(
        channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
    )

    board_channel = DiscordChannel(channel_id=..., channel_name=...)
    ep2025_channel = DiscordChannel(channel_id=..., channel_name=...)
    em_channel = DiscordChannel(channel_id=..., channel_name=...)
    website_channel = DiscordChannel(channel_id=..., channel_name=...)
    bot_channel = DiscordChannel(channel_id=..., channel_name=...)


def discord_channel_router(wh: Webhook) -> DiscordChannel:

    if wh.source == "github":
        return github_router(wh)

    elif wh.source == "internal":
        return internal_router(wh)

    return dont_send_it


def github_router(wh: Webhook) -> DiscordChannel:

    gwh = GithubWebhook.from_webhook(wh)
    project = gwh.get_project()
    repository = gwh.get_repository()

    # We have three github projects, that we want to route to three different
    # channels - one for ep2025, one for EM, and one for the board.
    if project == GithubProjects.board_project:
        return Channels.board_channel

    elif project == GithubProjects.ep2025_project:
        return Channels.ep2025_channel

    elif project == GithubProjects.em_project:
        return Channels.em_channel

    else:
        ...

    # Then we have our open source repositories, like website, this bot, and
    # some others, that we also might want to route to different channels
    if repository == GithubRepositories.website_repo:
        return Channels.website_channel

    elif repository == GithubRepositories.bot_repo:
        return Channels.bot_channel

    elif repository == ...:
        ...

    # Finally, we can use this to drop notifications that we don't want to
    # support, by routing them to /dev/null
    return dont_send_it


def internal_router(wh: Webhook) -> DiscordChannel:
    # For now just send all the internal messages to a test channel
    return Channels.test_channel
