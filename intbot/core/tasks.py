import logging

from core.integrations.github import parse_github_webhook, prep_github_webhook
from core.integrations.zammad import prep_zammad_webhook
from core.bot.channel_router import discord_channel_router, dont_send_it
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

    elif wh.source == "zammad":
        process_zammad_webhook(wh)

    else:
        raise ValueError(f"Unsupported source {wh.source}")


def process_internal_webhook(wh: Webhook):
    if wh.source != "internal":
        raise ValueError("Incorrect wh.source = {wh.source}")

    channel = discord_channel_router(wh)

    DiscordMessage.objects.create(
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
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

    if channel == dont_send_it:
        wh.processed_at = timezone.now()
        wh.save()
        return

    DiscordMessage.objects.create(
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
        content=f"GitHub: {parsed.as_discord_message()}",
        # Mark as unsent - to be sent with the next batch
        sent_at=None,
    )
    wh.processed_at = timezone.now()
    wh.save()


def process_zammad_webhook(wh: Webhook):
    if wh.source != "zammad":
        raise ValueError("Incorrect wh.source = {wh.source}")

    # Unlike in github, the zammad webhook is richer and
    # contains much more information, so no extra fetch is needed.
    # However, we can extract information and store it in the meta field, that
    # way we can reuse it later more easily.
    wh = prep_zammad_webhook(wh)
    channel = discord_channel_router(wh)

    if channel == dont_send_it:
        wh.processed_at = timezone.now()
        wh.save()
        return

    DiscordMessage.objects.create(
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
        content=f"Zammad: {wh.meta['message']}",
        # Mark as unsent - to be sent with the next batch
        sent_at=None,
    )
    wh.processed_at = timezone.now()
    wh.save()
