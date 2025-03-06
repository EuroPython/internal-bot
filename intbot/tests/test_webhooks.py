import hashlib
import hmac
import json

import pytest
from core.models import Webhook
from django.conf import settings


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
        json.dumps(webhook_body),
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
        json.dumps(webhook_body),
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
        json.dumps(webhook_body),
        content_type="application/json",
        HTTP_AUTHORIZATION=settings.WEBHOOK_INTERNAL_TOKEN,
    )

    wh = Webhook.objects.get()
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "created"
    assert response.json()["guid"] == str(wh.uuid)


@pytest.mark.django_db
def test_github_webhook_endpoint_checks_authorization_token(client):
    webhook_body = {}
    response = client.post(
        "/webhook/github/",
        json.dumps(webhook_body),
        content_type="application/json",
    )

    assert response.status_code == 403
    assert response.content == "X-Hub-Signature-256 is missing".encode("utf-8")

def sign_github_webhook(webhook_body):
    hashed = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET_TOKEN.encode("utf-8"),
        msg=json.dumps(webhook_body).encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    signature = "sha256=" + hashed.hexdigest()

    return signature


@pytest.mark.django_db
def test_github_webhook_endpoint_fails_with_bad_token(client):
    webhook_body = {
        "event": "test1",
        "content": {
            "random": "content",
        },
    }

    response = client.post(
        "/webhook/github/",
        json.dumps(webhook_body),
        content_type="application/json",
        headers={"X-Hub-Signature-256": "bad signature"},
    )

    assert response.status_code == 403
    assert response.content == "Signatures don't match".encode("utf-8")
    assert True


@pytest.mark.django_db
def test_github_webhook_endpoint_works_with_correct_token(client):
    webhook_body = {
        "event": "test1",
        "content": {
            "random": "content",
        },
    }

    signature = sign_github_webhook(webhook_body)

    response = client.post(
        "/webhook/github/",
        json.dumps(webhook_body),
        content_type="application/json",
        headers={"X-Hub-Signature-256": signature},
    )
    assert response.status_code == 200
    wh = Webhook.objects.get()
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "created"
    assert response.json()["guid"] == str(wh.uuid)
    assert wh.source == "github"


def sign_zammad_webhook(webhook_body):
    hashed = hmac.new(
        settings.ZAMMAD_WEBHOOK_SECRET_TOKEN.encode("utf-8"),
        msg=json.dumps(webhook_body).encode("utf-8"),
        digestmod=hashlib.sha1,
    )
    signature = "sha1=" + hashed.hexdigest()

    return signature


@pytest.mark.django_db
def test_zammad_webhook_endpoint_checks_authorization_token(client):
    webhook_body = {}

    response = client.post(
        "/webhook/zammad/",
        json.dumps(webhook_body),
        content_type="application/json",
    )

    assert response.status_code == 403
    assert response.content == "X-Hub-Signature is missing".encode("utf-8")


@pytest.mark.django_db
def test_zammad_webhook_endpoint_fails_with_bad_token(client):
    webhook_body = {
        "event": "test1",
        "content": {
            "random": "content",
        },
    }

    response = client.post(
        "/webhook/zammad/",
        json.dumps(webhook_body),
        content_type="application/json",
        headers={"X-Hub-Signature": "bad signature"},
    )

    assert response.status_code == 403
    assert response.content == "Signatures don't match".encode("utf-8")


@pytest.mark.django_db
def test_zammad_webhook_endpoint_works_with_correct_token(client):
    webhook_body = {
        "event": "test1",
        "content": {
            "random": "content",
        },
    }

    signature = sign_zammad_webhook(webhook_body)

    response = client.post(
        "/webhook/zammad/",
        json.dumps(webhook_body),
        content_type="application/json",
        headers={"X-Hub-Signature": signature},
    )
    assert response.status_code == 200
    wh = Webhook.objects.get()
    assert response["Content-Type"] == "application/json"
    assert response.json()["status"] == "created"
    assert response.json()["guid"] == str(wh.uuid)
    assert wh.source == "zammad"
