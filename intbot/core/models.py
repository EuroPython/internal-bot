import uuid

from django.db import models


class Webhook(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)

    source = models.CharField(max_length=255)
    event = models.CharField(max_length=255)

    # Cryptographic signature of the webhook
    signature = models.CharField(max_length=255)

    # Extra information about the webhook, that might be provided in the
    # headers or similar
    meta = models.JSONField(default=dict)

    content = models.JSONField()

    # Sometimes processing the webhook requires setting up or downloading extra
    # information from other sources. This is the field to put that data in.
    extra = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.uuid}"


class DiscordMessage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)

    # This is intentionally char field, even if discord.py requires later to
    # cast it to int
    channel_id = models.CharField(max_length=255)
    # Channel name at the time of scheduling the message
    channel_name = models.CharField(max_length=255)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # To delay messages to be sent after certain timestmap in the future
    send_after = models.DateTimeField(blank=True, null=True)

    # Messages to be sent have null here
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.uuid} {self.content[:30]}"
