import pytest
import respx
from core.integrations import pretalx
from core.models import PretalxData
from httpx import Response


def submissions_pages_generator(url):
    """
    Generator to simulate pagination.

    Extracted to a generator because we use it in multiple places
    """
    yield Response(
        200,
        json={
            "results": [
                {"hello": "world"},
            ],
            "next": f"{url}&page=2",
        },
    )

    yield Response(
        200,
        json={
            "results": [
                {"foo": "bar"},
            ],
            # It's important to make it last page in tests.
            # Otherwise it will be infinite loop :)
            "next": None,
        },
    )


def speaker_pages_generator(url):
    """
    Generator to simulate pagination.

    Extracted to a generator because we use it in multiple places
    """
    yield Response(
        200,
        json={
            "results": [
                {"hello": "world"},
            ],
            "next": f"{url}&page=2",
        },
    )

    yield Response(
        200,
        json={
            "results": [
                {"foo": "bar"},
            ],
            # It's important to make it last page in tests.
            # Otherwise it will be infinite loop :)
            "next": None,
        },
    )


@respx.mock
def test_fetch_submissions_from_pretalx():
    url = "https://pretalx.com/api/events/europython-2025/submissions/?questions=all"
    data = submissions_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    submissions = pretalx.fetch_pretalx_data(
        "europython-2025",
        PretalxData.PretalxResources.submissions,
    )

    assert submissions == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
def test_fetch_speakers_from_pretalx():
    url = "https://pretalx.com/api/events/europython-2025/speakers/?questions=all"
    data = speaker_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    submissions = pretalx.fetch_pretalx_data(
        "europython-2025",
        PretalxData.PretalxResources.speakers,
    )

    assert submissions == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
@pytest.mark.django_db
def test_download_latest_submissions():
    url = "https://pretalx.com/api/events/europython-2025/submissions/?questions=all"
    data = submissions_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    pretalx.download_latest_submissions("europython-2025")

    pd = PretalxData.objects.get(resource=PretalxData.PretalxResources.submissions)
    assert pd.resource == "submissions"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
@pytest.mark.django_db
def test_download_latest_speakers():
    url = "https://pretalx.com/api/events/europython-2025/speakers/?questions=all"
    data = speaker_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    pretalx.download_latest_speakers("europython-2025")

    pd = PretalxData.objects.get(resource=PretalxData.PretalxResources.speakers)
    assert pd.resource == "speakers"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]
