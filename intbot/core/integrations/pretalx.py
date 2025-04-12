from typing import Any

import httpx
from core.models import PretalxData
from django.conf import settings

PRETALX_EVENT = "ep2025"
base_url = f"https://pretalx.com/api/events/{PRETALX_EVENT}/"

RESOURCES = {
    # Questions need to be passed to include answers in the same endpoint,
    # saving us later time with joining the answers.
    PretalxData.PretalxEndpoints.submissions: "submissions?questions=all",
    PretalxData.PretalxEndpoints.speakers: "speakers?questions=all",
}


JsonType = dict[str, Any]


def fetch_pretalx_data(resource) -> list[JsonType]:
    headers = {
        "Authorization": f"Token {settings.PRETALX_API_TOKEN}",
        "Content-Type": "application/json",
    }

    endpoint = RESOURCES[resource]
    url = base_url + f"{endpoint}"

    # Pretalx paginates the output, so we will need to do multiple requests and
    # then merge mutliple pages to one big dictionary
    res0 = []
    data = {"next": url}
    n = 0
    while url := data["next"]:
        n += 1
        response = httpx.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        data = response.json()
        res0 += data["results"]

    return res0


def download_latest_submissions() -> PretalxData:
    data = fetch_pretalx_data(PretalxData.PretalxEndpoints.submissions)

    pretalx_data = PretalxData.objects.create(
        endpoint=PretalxData.PretalxEndpoints.submissions,
        content=data,
    )

    return pretalx_data


def download_latest_speakers() -> PretalxData:
    data = fetch_pretalx_data(PretalxData.PretalxEndpoints.speakers)

    pretalx_data = PretalxData.objects.create(
        endpoint=PretalxData.PretalxEndpoints.speakers,
        content=data,
    )

    return pretalx_data
