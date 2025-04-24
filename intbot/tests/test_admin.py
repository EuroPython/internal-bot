"""
Sanity checks (mostly) if the admin resources are available
"""

from core.models import DiscordMessage, PretalxData, Webhook


def test_admin_for_webhooks_sanity_check(admin_client):
    url = "/admin/core/webhook/"
    wh = Webhook.objects.create(content={}, extra={})
    assert wh.uuid

    response = admin_client.get(url)

    assert response.status_code == 200
    assert str(wh.uuid).encode() in response.content
    assert wh.source.encode() in response.content
    assert wh.event.encode() in response.content


def test_admin_for_discordmessages_sanity_check(admin_client):
    url = "/admin/core/discordmessage/"
    dm = DiscordMessage.objects.create(
        channel_id="12345",
        channel_name="#test",
    )
    assert dm.uuid

    response = admin_client.get(url)

    assert response.status_code == 200
    assert str(dm.uuid).encode() in response.content
    assert dm.channel_id.encode() in response.content
    assert dm.channel_name.encode() in response.content


def test_admin_list_for_pretalx_data(admin_client):
    """Simple sanity check if the page loads correctly"""
    url = "/admin/core/pretalxdata/"
    pd = PretalxData.objects.create(
        resource=PretalxData.PretalxResources.speakers,
        content={},
    )
    assert pd.uuid

    response = admin_client.get(url)

    assert response.status_code == 200
    assert str(pd.uuid).encode() in response.content
    assert pd.get_resource_display().encode() in response.content


def test_admin_change_for_pretalx_data(admin_client):
    """Simple sanity check if the page loads correctly"""
    url = "/admin/core/pretalxdata/"
    pd = PretalxData.objects.create(
        resource=PretalxData.PretalxResources.speakers,
        content={},
    )
    assert pd.uuid

    response = admin_client.get(f"{url}{pd.pk}/change/")

    assert response.status_code == 200
    assert str(pd.uuid).encode() in response.content
    assert pd.get_resource_display().encode() in response.content
