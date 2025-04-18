from core.integrations.pretalx import (
    PRETALX_EVENTS,
    download_latest_speakers,
    download_latest_submissions,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Downloads latest pretalx data"

    def add_arguments(self, parser):
        # Add keyword argument event
        parser.add_argument(
            "--event",
            choices=PRETALX_EVENTS,
            help="slug of the event (for example `europython-2025`)",
            required=True,
        )

    def handle(self, **kwargs):
        event = kwargs["event"]

        self.stdout.write(f"Downloading latest speakers from pretalx... {event}")
        download_latest_speakers(event)

        self.stdout.write(f"Downloading latest submissions from pretalx... {event}")
        download_latest_submissions(event)
