from django.core.management.base import BaseCommand

from core.bot.scheduled_messages import MESSAGE_FACTORIES


class Command(BaseCommand):
    help = "Sends a scheduled message to Discord"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            required=True,
            choices=MESSAGE_FACTORIES.keys(),
            help="Message type to send"
        )
        
    def handle(self, *args, **options):
        message_type = options["type"]
        
        factory = MESSAGE_FACTORIES[message_type]
        message = factory()
        message.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduled '{message_type}' message for channel {message.channel_name}"
            )
        )