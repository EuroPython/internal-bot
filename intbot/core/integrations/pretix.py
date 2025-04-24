import logging
from typing import Any

import httpx
from core.models import PretixData
from django.conf import settings

logger = logging.getLogger(__name__)

PRETALX_EVENTS = [
    "2022",
    "ep2023",
    "ep2024",
    "ep2025",
]

ENDPOINTS = {
    # Questions need to be passed to include answers in the same endpoint,
    # saving us later time with joining the answers.
    PretixData.PretixResources.orders: "orders/",
    PretixData.PretixResources.products: "items/",
    PretixData.PretixResources.vouchers: "vouchers/",
}


JsonType = dict[str, Any]


def get_event_url(event):
    assert event in PRETALX_EVENTS

    pretix_url = "https://tickets.europython.eu"
    url = f"{pretix_url}/api/v1/organizers/europython/events/{event}/"
    return url


def fetch_pretix_data(
    event: str, resource: PretixData.PretixResources
) -> list[JsonType]:
    headers = {
        "Authorization": f"Token {settings.PRETIX_API_TOKEN}",
        "Content-Type": "application/json",
    }

    base_url = get_event_url(event)
    endpoint = ENDPOINTS[resource]
    url = f"{base_url}{endpoint}"

    # Pretalx paginates the output, so we will need to do multiple requests and
    # then merge multiple pages to one big dictionary
    results = []
    page = 0

    # This takes advantage of the fact that url will contain a url to the
    # next page, until there is more data to fetch. If this is the last page,
    # then the url will be None (falsy), and thus stop the while loop.
    while url:
        page += 1
        response = httpx.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        logger.info("Fetching data from %s, page %s", url, page)

        data = response.json()
        results += data["results"]
        url = data["next"]

    return results


def download_latest_orders(event: str) -> PretixData:
    data = fetch_pretix_data(event, PretixData.PretixResources.orders)

    pretix_data = PretixData.objects.create(
        resource=PretixData.PretixResources.orders,
        content=data,
    )

    return pretix_data

def download_latest_products(event: str) -> PretixData:
    data = fetch_pretix_data(event, PretixData.PretixResources.products)

    pretix_data = PretixData.objects.create(
        resource=PretixData.PretixResources.products,
        content=data,
    )

    return pretix_data

def download_latest_vouchers(event: str) -> PretixData:
    data = fetch_pretix_data(event, PretixData.PretixResources.vouchers)

    pretix_data = PretixData.objects.create(
        resource=PretixData.PretixResources.vouchers,
        content=data,
    )

    return pretix_data
