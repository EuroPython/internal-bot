from django.conf import settings

from core.models import DiscordMessage, Webhook
from django.utils import timezone
from django_tasks import task


@task
def process_webhook(wh_uuid: str):
    wh = Webhook.objects.get(uuid=wh_uuid)

    if wh.source == "internal":
        process_internal_webhook(wh)

    else:
        raise ValueError(f"Unsupported source {wh.source}")


def process_internal_webhook(wh: Webhook):
    if wh.source != "internal":
        raise ValueError("Incorrect wh.source = {wh.source}")

    DiscordMessage.objects.create(
        channel_id=settings.DISCORD_TEST_CHANNEL_ID,
        channel_name=settings.DISCORD_TEST_CHANNEL_NAME,
        content=f"Webhook content: {wh.content}",
        # Mark as unsend - to be sent with the next batch
        sent_at=None,
    )
    wh.processed_at = timezone.now()
    wh.save()
