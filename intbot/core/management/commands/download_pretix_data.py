from core.integrations.pretalx import (
    PRETIX_EVENTS,
    download_latest_orders,
    download_latest_products,
    download_latest_vouchers,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Downloads latest pretix data"

    def add_arguments(self, parser):
        # Add keyword argument event
        parser.add_argument(
            "--event",
            choices=PRETIX_EVENTS,
            help="slug of the event (for example `ep2025`)",
            required=True,
        )

    def handle(self, **kwargs):
        event = kwargs["event"]

        self.stdout.write(f"Downloading latest products from pretix... {event}")
        download_latest_products(event)

        self.stdout.write(f"Downloading latest vouchers from pretix... {event}")
        download_latest_vouchers(event)

        self.stdout.write(f"Downloading latest orders from pretix... {event}")
        download_latest_orders(event)
