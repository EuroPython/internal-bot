"""
This file is currently used to test the test harness.

It checks whether the tests are running, can access databse, etc
"""

from django.contrib.auth.models import User
import pytest


@pytest.mark.django_db
def test_database_sanity_check():
    u = User.objects.create(username="Poirot")

    assert u.id
    assert u.username == "Poirot"
