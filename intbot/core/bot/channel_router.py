"""
Channel router that decides where to send particular message
"""

from dataclasses import dataclass

from core.integrations.github import (
    GithubProjects,
    GithubRepositories,
    parse_github_webhook,
)
from core.integrations.zammad import ZammadConfig
from core.models import Webhook
from django.conf import settings


@dataclass
class DiscordChannel:
    channel_id: str
    channel_name: str


dont_send_it = DiscordChannel(channel_id="0", channel_name="DONT_SEND_IT")


class Channels:
    # Github
    test_channel = DiscordChannel(
        channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
    )

    board_channel = DiscordChannel(
        channel_id=settings.DISCORD_BOARD_CHANNEL_ID,
        channel_name=settings.DISCORD_BOARD_CHANNEL_NAME,
    )
    ep2025_channel = DiscordChannel(
        channel_id=settings.DISCORD_EP2025_CHANNEL_ID,
        channel_name=settings.DISCORD_EP2025_CHANNEL_NAME,
    )
    em_channel = DiscordChannel(
        channel_id=settings.DISCORD_EM_CHANNEL_ID,
        channel_name=settings.DISCORD_EM_CHANNEL_NAME,
    )
    website_channel = DiscordChannel(
        channel_id=settings.DISCORD_WEBSITE_CHANNEL_ID,
        channel_name=settings.DISCORD_WEBSITE_CHANNEL_NAME,
    )
    bot_channel = DiscordChannel(
        channel_id=settings.DISCORD_BOT_CHANNEL_ID,
        channel_name=settings.DISCORD_BOT_CHANNEL_NAME,
    )

    # Zammad
    billing_channel = DiscordChannel(
        channel_id=settings.DISCORD_BILLING_CHANNEL_ID,
        channel_name=settings.DISCORD_BILLING_CHANNEL_NAME,
    )
    helpdesk_channel = DiscordChannel(
        channel_id=settings.DISCORD_HELPDESK_CHANNEL_ID,
        channel_name=settings.DISCORD_HELPDESK_CHANNEL_NAME,
    )
    programme_channel = DiscordChannel(
        channel_id=settings.DISCORD_PROGRAMME_CHANNEL_ID,
        channel_name=settings.DISCORD_PROGRAMME_CHANNEL_NAME,
    )
    finaid_channel = DiscordChannel(
        channel_id=settings.DISCORD_FINAID_CHANNEL_ID,
        channel_name=settings.DISCORD_FINAID_CHANNEL_NAME,
    )
    sponsors_channel = DiscordChannel(
        channel_id=settings.DISCORD_SPONSORS_CHANNEL_ID,
        channel_name=settings.DISCORD_SPONSORS_CHANNEL_NAME,
    )
    grants_channel = DiscordChannel(
        channel_id=settings.DISCORD_GRANTS_CHANNEL_ID,
        channel_name=settings.DISCORD_GRANTS_CHANNEL_NAME,
    )


def discord_channel_router(wh: Webhook) -> DiscordChannel:
    if wh.source == "github":
        return github_router(wh)

    elif wh.source == "zammad":
        return zammad_router(wh)

    elif wh.source == "internal":
        return internal_router(wh)

    return dont_send_it


def github_router(wh: Webhook) -> DiscordChannel:
    gwh = parse_github_webhook(wh)
    project = gwh.get_project()
    repository = gwh.get_repository()

    # We have three github projects, that we want to route to three different
    # channels - one for ep2025, one for EM, and one for the board.
    PROJECTS = {
        GithubProjects.board_project: Channels.board_channel,
        GithubProjects.ep2025_project: Channels.ep2025_channel,
        GithubProjects.em_project: Channels.em_channel,
    }

    if channel := PROJECTS.get(project.id):
        return channel

    # Then we have our open source repositories, like website, this bot, and
    # some others, that we also might want to route to different channels
    REPOSITORIES = {
        GithubRepositories.website_repo: Channels.website_channel,
        GithubRepositories.bot_repo: Channels.bot_channel,
    }

    if channel := REPOSITORIES.get(repository.id):
        return channel

    # Finally, we can use this to drop notifications that we don't want to
    # support, by not sending them.
    return dont_send_it


def zammad_router(wh: Webhook) -> DiscordChannel:
    groups = {
        ZammadConfig.helpdesk_group: Channels.helpdesk_channel,
        ZammadConfig.billing_group: Channels.billing_channel,
        ZammadConfig.programme_group: Channels.programme_channel,
        ZammadConfig.finaid_group: Channels.finaid_channel,
        ZammadConfig.sponsors_group: Channels.sponsors_channel,
        ZammadConfig.grants_group: Channels.grants_channel,
    }

    if channel := groups.get(wh.extra["group"]):
        return channel

    # If it doesn't match any of the groups, just skip it
    return dont_send_it


def internal_router(wh: Webhook) -> DiscordChannel:
    # For now just send all the internal messages to a test channel
    return Channels.test_channel
