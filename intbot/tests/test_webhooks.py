import pytest
from django.conf import settings
from core.models import Webhook

@pytest.mark.django_db
def test_internal_wh_endpoint_checks_authorization_token(client):
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

    assert response.status_code == 403
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "bad"
    assert response.json()["message"] == "Authorization token is missing"

@pytest.mark.django_db
def test_internal_wh_endpoint_fails_with_bad_token(client):
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
        HTTP_AUTHORIZATION="random-incorrect-token",
    )

    assert response.status_code == 403
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "bad"
    assert response.json()["message"] == "Token doesn't match"

@pytest.mark.django_db
def test_internal_wh_endpoint_works_with_correct_token(client):
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
        HTTP_AUTHORIZATION=settings.WEBHOOK_INTERNAL_TOKEN,
    )

    wh = Webhook.objects.get()
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "created"
    assert response.json()["guid"] == str(wh.uuid)
