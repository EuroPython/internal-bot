import pytest
from core.models import Webhook


@pytest.mark.django_db
def test_database_sanity_check(client):
    webhook_body = {
        "event": "test1",
        "content": {
            "random": "content",
        },
    }

    response = client.post(
        "/webhook/internal/",
        json=webhook_body,
        content_type="application/json",
    )

    wh = Webhook.objects.get()
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "created"
    assert response.json()["guid"] == str(wh.uuid)
