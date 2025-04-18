import logging
from typing import Any

import httpx
from core.models import PretalxData
from django.conf import settings

logger = logging.getLogger(__name__)

PRETALX_EVENTS = [
    "europython-2022",
    "europython-2023",
    "europython-2024",
    "europython-2025",
]

ENDPOINTS = {
    # Questions need to be passed to include answers in the same endpoint,
    # saving us later time with joining the answers.
    PretalxData.PretalxResources.submissions: "submissions/?questions=all",
    PretalxData.PretalxResources.speakers: "speakers/?questions=all",
}


JsonType = dict[str, Any]


def get_event_url(event):
    assert event in PRETALX_EVENTS

    return f"https://pretalx.com/api/events/{event}/"


def fetch_pretalx_data(
    event: str, resource: PretalxData.PretalxResources
) -> list[JsonType]:
    headers = {
        "Authorization": f"Token {settings.PRETALX_API_TOKEN}",
        "Content-Type": "application/json",
    }

    base_url = get_event_url(event)
    endpoint = ENDPOINTS[resource]
    url = f"{base_url}{endpoint}"

    # Pretalx paginates the output, so we will need to do multiple requests and
    # then merge multiple pages to one big dictionary
    results = []
    data = {"next": url}
    page = 0

    # This takes advantage of the fact that "next" will contain a url to the
    # next page, until there is more data to fetch. If this is the last page,
    # then the data["next"] will be None (falsy), and thus stop the while loop.
    while url := data["next"]:
        page += 1
        response = httpx.get(url, headers=headers)

        if response.status_code != 200:
            breakpoint()
            raise Exception(f"Error {response.status_code}: {response.text}")

        logger.info("Fetching data from %s, page %s", url, page)

        data = response.json()
        results += data["results"]

    return results


def download_latest_submissions(event: str) -> PretalxData:
    data = fetch_pretalx_data(event, PretalxData.PretalxResources.submissions)

    pretalx_data = PretalxData.objects.create(
        resource=PretalxData.PretalxResources.submissions,
        content=data,
    )

    return pretalx_data


def download_latest_speakers(event: str) -> PretalxData:
    data = fetch_pretalx_data(event, PretalxData.PretalxResources.speakers)

    pretalx_data = PretalxData.objects.create(
        resource=PretalxData.PretalxResources.speakers,
        content=data,
    )

    return pretalx_data
