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

    # Messages to be have null here
    sent_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.uuid} {self.content[:30]}"


class InboxItem(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)

    # Discord message details
    message_id = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    channel_name = models.CharField(max_length=255)
    server_id = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    # User who added the message to their inbox
    user_id = models.CharField(max_length=255)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def url(self) -> str:
        """Return URL to the Discord message"""
        return f"https://discord.com/channels/{self.server_id}/{self.channel_id}/{self.message_id}"

    def summary(self) -> str:
        """Return a summary of the inbox item for use in Discord messages"""
        timestamp = self.created_at.strftime("%Y-%m-%d %H:%M")
        return (
            f"`{timestamp}` | from **{self.author}** @ **{self.channel_name}**: "
            f"[{self.content[:30]}...]({self.url()})"
        )

    def __str__(self):
        return f"{self.uuid} {self.author}: {self.content[:30]}"


class PretalxData(models.Model):
    """
    Table to store raw data download from pretalx for later parsing.

    We first download data from pretalx to this table, and then fire a separate
    background task that pulls data from this table and stores in separate
    "business" tables, like "Proposal" or "Speaker".
    """

    class PretalxEndpoints(models.TextChoices):
        submissions = "submissions", "Submissions"
        speakers = "speakers", "Speakers"
        schedule = "schedule", "Schedule"

    uuid = models.UUIDField(default=uuid.uuid4)
    endpoint = models.CharField(
        max_length=255,
        choices=PretalxEndpoints.choices,
    )
    content = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.uuid}"
