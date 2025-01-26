import logging

from core.integrations.github import parse_github_webhook, prep_github_webhook
from core.bot.channel_router import discord_channel_router
from core.models import DiscordMessage, Webhook
from django.utils import timezone
from django_tasks import task

logger = logging.getLogger()


@task
def process_webhook(wh_uuid: str):
    wh = Webhook.objects.get(uuid=wh_uuid)

    if wh.source == "internal":
        process_internal_webhook(wh)

    elif wh.source == "github":
        process_github_webhook(wh)

    else:
        raise ValueError(f"Unsupported source {wh.source}")


def process_internal_webhook(wh: Webhook):
    if wh.source != "internal":
        raise ValueError("Incorrect wh.source = {wh.source}")

    channel = discord_channel_router(wh)

    DiscordMessage.objects.create(
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
        # channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        # channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
        content=f"Webhook content: {wh.content}",
        # Mark as not sent - to be sent with the next batch
        sent_at=None,
    )
    wh.processed_at = timezone.now()
    wh.save()


def process_github_webhook(wh: Webhook):
    if wh.source != "github":
        raise ValueError("Incorrect wh.source = {wh.source}")

    try:
        wh = prep_github_webhook(wh)
    except ValueError as e:
        # Downgrading to info because it's most likely event not supported
        logger.info(f"Not processing Github Webhook {wh.uuid}: {e}")
        return

    parsed = parse_github_webhook(wh)
    channel = discord_channel_router(wh)

    DiscordMessage.objects.create(
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
        # channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        # channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
        content=f"GitHub: {parsed.message}",
        # Mark as unsend - to be sent with the next batch
        sent_at=None,
    )
    wh.event = parsed.event_action
    wh.processed_at = timezone.now()
    wh.save()
