from core.bot.main import run_bot
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the discord bot"

    def handle(self, *args, **kwargs):
        run_bot()
