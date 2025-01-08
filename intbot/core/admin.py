from django.contrib import admin

from core.models import Webhook, DiscordMessage

admin.site.register(Webhook)
admin.site.register(DiscordMessage)
