import respx
import pytest
from core.integrations import pretalx
from core.models import PretalxData
from httpx import Response


@respx.mock
def test_fetch_submissions_from_pretalx():
    endpoint = pretalx.RESOURCES[PretalxData.PretalxEndpoints.submissions]
    url = pretalx.base_url + endpoint
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "results": [
                    {"hello": "world"},
                ],
                "next": f"{url}&page=2",
            },
        )
    )
    respx.get(url + "&page=2").mock(
        return_value=Response(
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
    )

    submissions = pretalx.fetch_pretalx_data(
        PretalxData.PretalxEndpoints.submissions,
    )

    assert submissions == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
def test_fetch_speakers_from_pretalx():
    endpoint = pretalx.RESOURCES[PretalxData.PretalxEndpoints.speakers]
    url = pretalx.base_url + endpoint
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "results": [
                    {"hello": "world"},
                ],
                "next": f"{url}&page=2",
            },
        )
    )
    respx.get(url + "&page=2").mock(
        return_value=Response(
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
    )

    submissions = pretalx.fetch_pretalx_data(
        PretalxData.PretalxEndpoints.speakers,
    )

    assert submissions == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
@pytest.mark.django_db
def test_download_latest_submissions():
    endpoint = pretalx.RESOURCES[PretalxData.PretalxEndpoints.submissions]
    url = pretalx.base_url + endpoint
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "results": [
                    {"hello": "world"},
                ],
                "next": f"{url}&page=2",
            },
        )
    )
    respx.get(url + "&page=2").mock(
        return_value=Response(
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
    )

    pretalx.download_latest_submissions()

    pd = PretalxData.objects.get(endpoint=PretalxData.PretalxEndpoints.submissions)

    assert pd.endpoint == "submissions"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]

@respx.mock
@pytest.mark.django_db
def test_download_latest_speakers():
    endpoint = pretalx.RESOURCES[PretalxData.PretalxEndpoints.speakers]
    url = pretalx.base_url + endpoint
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "results": [
                    {"hello": "world"},
                ],
                "next": f"{url}&page=2",
            },
        )
    )
    respx.get(url + "&page=2").mock(
        return_value=Response(
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
    )

    pretalx.download_latest_speakers()

    pd = PretalxData.objects.get(endpoint=PretalxData.PretalxEndpoints.speakers)

    assert pd.endpoint == "speakers"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]

