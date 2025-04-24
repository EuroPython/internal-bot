import json

from core.models import DiscordMessage, PretalxData, Webhook
from django.contrib import admin
from django.utils.html import format_html


class WebhookAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "source",
        "event",
        "created_at",
        "modified_at",
    ]
    list_filter = ["created_at"]
    readonly_fields = fields = [
        "uuid",
        "source",
        "event",
        "signature",
        "pretty_meta",
        "pretty_content",
        "created_at",
        "modified_at",
        "processed_at",
    ]

    def pretty_meta(self, obj: Webhook):
        return format_html("<pre>{}</pre>", json.dumps(obj.meta, indent=4))

    pretty_meta.short_description = "Meta"

    def pretty_content(self, obj: Webhook):
        return format_html("<pre>{}</pre>", json.dumps(obj.content, indent=4))

    pretty_content.short_description = "Content"


class DiscordMessageAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "channel_name",
        "content_short",
        "channel_id",
        "created_at",
        "modified_at",
        "sent_at",
    ]
    list_filter = [
        "created_at",
        "sent_at",
        "channel_name",
    ]
    readonly_fields = fields = [
        "uuid",
        "channel_id",
        "content",
        "created_at",
        "modified_at",
        "sent_at",
    ]

    def content_short(self, obj: DiscordMessage):
        # NOTE(artcz) This can create false shortcuts, but for most messages is
        # good enough, because most of them are longer than 20 chars
        return f"{obj.content[:10]}...{obj.content[-10:]}"


class PretalxDataAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "resource",
        "created_at",
        "modified_at",
    ]
    list_filter = [
        "created_at",
        "resource",
    ]
    readonly_fields = fields = [
        "uuid",
        "resource",
        "pretty_content",
        "created_at",
        "modified_at",
        "processed_at",
    ]

    def pretty_content(self, obj: PretalxData):
        return format_html("<pre>{}</pre>", json.dumps(obj.content, indent=4))

    pretty_content.short_description = "Content"


admin.site.register(Webhook, WebhookAdmin)
admin.site.register(DiscordMessage, DiscordMessageAdmin)
admin.site.register(PretalxData, PretalxDataAdmin)
