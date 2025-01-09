from core.models import DiscordMessage, Webhook
from core.integrations.github import parse_github_webhook
from django.conf import settings
from django.utils import timezone
from django_tasks import task


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

    DiscordMessage.objects.create(
        channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
        content=f"Webhook content: {wh.content}",
        # Mark as not sent - to be sent with the next batch
        sent_at=None,
    )
    wh.processed_at = timezone.now()
    wh.save()


def process_github_webhook(wh: Webhook):
    if wh.source != "github":
        raise ValueError("Incorrect wh.source = {wh.source}")

    message, event_action = parse_github_webhook(headers=wh.meta, content=wh.content)

    # NOTE WHERE SHOULD WE GET THE CHANNEL ID FROM?
    DiscordMessage.objects.create(
        channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
        content=f"GitHub: {message}",
        # Mark as unsend - to be sent with the next batch
        sent_at=None,
    )
    wh.event = event_action
    wh.processed_at = timezone.now()
    wh.save()
