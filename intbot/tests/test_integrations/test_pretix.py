import pytest
import respx
from core.integrations import pretix
from core.models import PretixData
from httpx import Response


def orders_pages_generator(url):
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


def vouchers_pages_generator(url):
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


def products_pages_generator(url):
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
def test_fetch_orders_from_pretix():
    url = "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/orders/"
    data = orders_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    orders = pretix.fetch_pretix_data(
        "ep2025",
        PretixData.PretixResources.orders,
    )

    assert orders == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
def test_fetch_vouchers_from_pretix():
    url = "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/vouchers/"
    data = vouchers_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    orders = pretix.fetch_pretix_data(
        "ep2025",
        PretixData.PretixResources.vouchers,
    )

    assert orders == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
def test_fetch_products_from_pretix():
    url = "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/items/"
    data = products_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    orders = pretix.fetch_pretix_data(
        "ep2025",
        PretixData.PretixResources.products,
    )

    assert orders == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
@pytest.mark.django_db
def test_download_latest_orders():
    url = "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/orders/"
    data = orders_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    pretix.download_latest_orders("ep2025")

    pd = PretixData.objects.get(resource=PretixData.PretixResources.orders)
    assert pd.resource == "orders"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
@pytest.mark.django_db
def test_download_latest_products():
    url = "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/items/"
    data = orders_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    pretix.download_latest_products("ep2025")

    pd = PretixData.objects.get(resource=PretixData.PretixResources.products)
    assert pd.resource == "products"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]


@respx.mock
@pytest.mark.django_db
def test_download_latest_vouchers():
    url = "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/vouchers/"
    data = orders_pages_generator(url)
    respx.get(url).mock(return_value=next(data))
    respx.get(url + "&page=2").mock(return_value=next(data))

    pretix.download_latest_vouchers("ep2025")

    pd = PretixData.objects.get(resource=PretixData.PretixResources.vouchers)
    assert pd.resource == "vouchers"
    assert pd.content == [
        {"hello": "world"},
        {"foo": "bar"},
    ]
