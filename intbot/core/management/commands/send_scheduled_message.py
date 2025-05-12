from core.bot.scheduled_messages import MESSAGE_FACTORIES
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sends a scheduled message to Discord"

    def add_arguments(self, parser):
        parser.add_argument(
            "--template",
            required=True,
            choices=MESSAGE_FACTORIES.keys(),
            help="Message template to send",
        )

    def handle(self, *args, **options):
        message_template = options["template"]

        factory = MESSAGE_FACTORIES[message_template]
        message = factory()
        message.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduled '{message_template}' message for channel {message.channel_name}"
            )
        )
