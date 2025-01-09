"""
This file is currently used to test the test harness.

It checks whether the tests
 * are running
 * can access databse
 * can reach the views
 * can authenticate,
 * etc

"""

from django.contrib.auth.models import User
from django.conf import settings
import pytest


@pytest.mark.django_db
def test_database_sanity_check():
    u = User.objects.create(username="Poirot")

    assert u.id
    assert u.username == "Poirot"


def test_http_sanity_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json()["hello"] == "world"
    assert response.json()["v"] == settings.APP_VERSION
