import pytest
import respx
from core.models import PretalxData, PretixData
from django.core.management import call_command
from httpx import Response


@respx.mock
@pytest.mark.django_db
def test_download_pretalx_data_command(capsys):
    for url in [
        "https://pretalx.com/api/events/europython-2025/submissions/?questions=all",
        "https://pretalx.com/api/events/europython-2025/speakers/?questions=all",
    ]:
        respx.get(url).mock(
            return_value=Response(200, json={"results": [], "next": None})
        )

    call_command("download_pretalx_data", event="europython-2025")

    # Minimal sanity checks
    stdout, stderr = capsys.readouterr()  # capture stdout / stderr
    assert "Downloading latest speakers" in stdout
    assert "Downloading latest submissions" in stdout
    assert (
        PretalxData.objects.get(
            resource=PretalxData.PretalxResources.submissions
        ).content
        == []
    )
    assert (
        PretalxData.objects.get(resource=PretalxData.PretalxResources.speakers).content
        == []
    )


@respx.mock
@pytest.mark.django_db
def test_download_pretix_data_command(capsys):
    for url in [
        "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/orders/",
        "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/items/",
        "https://tickets.europython.eu/api/v1/organizers/europython/events/ep2025/vouchers/",
    ]:
        respx.get(url).mock(
            return_value=Response(200, json={"results": [], "next": None})
        )

    call_command("download_pretix_data", event="ep2025")

    # Minimal sanity checks
    stdout, stderr = capsys.readouterr()  # capture stdout / stderr
    assert "Downloading latest products" in stdout
    assert "Downloading latest vouchers" in stdout
    assert "Downloading latest orders" in stdout
    assert (
        PretixData.objects.get(resource=PretixData.PretixResources.orders).content == []
    )
    assert (
        PretixData.objects.get(resource=PretixData.PretixResources.vouchers).content
        == []
    )
    assert (
        PretixData.objects.get(resource=PretixData.PretixResources.products).content
        == []
    )
