from unittest.mock import Mock

import pytest
from core.auth import EuroPythonSocialAccountAdapter
from django.test import RequestFactory


class TestEuroPythonSocialAccountAdapter:
    def _make_sociallogin(self, email: str) -> Mock:
        sociallogin = Mock()
        sociallogin.user.email = email
        return sociallogin

    def test_allows_europython_eu_email(self):
        adapter = EuroPythonSocialAccountAdapter()
        request = RequestFactory().get("/")
        sociallogin = self._make_sociallogin("user@europython.eu")

        assert adapter.is_open_for_signup(request, sociallogin) is True

    def test_rejects_other_domain(self):
        adapter = EuroPythonSocialAccountAdapter()
        request = RequestFactory().get("/")
        sociallogin = self._make_sociallogin("user@gmail.com")

        assert adapter.is_open_for_signup(request, sociallogin) is False

    def test_rejects_similar_domain(self):
        adapter = EuroPythonSocialAccountAdapter()
        request = RequestFactory().get("/")
        sociallogin = self._make_sociallogin("user@noteuropython.eu")

        assert adapter.is_open_for_signup(request, sociallogin) is False


@pytest.mark.django_db
class TestNoAccessView:
    def test_no_access_returns_403(self, client):
        response = client.get("/no-access/")

        assert response.status_code == 403

    def test_no_access_uses_template(self, client):
        response = client.get("/no-access/")

        assert "no_access.html" in [t.name for t in response.templates]


@pytest.mark.django_db
class TestLoginPage:
    def test_login_page_renders(self, client):
        response = client.get("/accounts/login/")

        assert response.status_code == 200
        assert b"Sign in with Google" in response.content
