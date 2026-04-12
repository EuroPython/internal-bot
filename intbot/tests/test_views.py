import pytest
from core.models import PretalxData, PretixData
from django.contrib.auth.models import User
from pytest_django.asserts import assertRedirects, assertTemplateUsed


def test_days_until_view(client):
    response = client.get("/days-until/")

    assert response.status_code == 200
    assertTemplateUsed(response, "days_until.html")


@pytest.mark.django_db
class TestPorductsView:
    def test_products_view_requires_login(self, client):
        response = client.get("/products/")

        assertRedirects(
            response,
            "/accounts/login/?next=/products/",
            fetch_redirect_response=False,
        )
        assert response.status_code == 302

    def test_products_non_staff_redirects_to_no_access(self, client):
        user = User.objects.create_user(username="regular", password="pass")
        client.force_login(user)

        response = client.get("/products/")

        assertRedirects(response, "/no-access/", target_status_code=403)

    def test_products_sanity_check(self, admin_client):
        PretixData.objects.create(
            resource=PretixData.PretixResources.products, content=[]
        )

        response = admin_client.get("/products/")

        assert response.status_code == 200
        assertTemplateUsed(response, "table.html")


@pytest.mark.django_db
class TestSubmissionsView:
    def test_submissions_view_requires_login(self, client):
        response = client.get("/submissions/")

        assertRedirects(
            response,
            "/accounts/login/?next=/submissions/",
            fetch_redirect_response=False,
        )

    def test_submissions_non_staff_redirects_to_no_access(self, client):
        user = User.objects.create_user(username="regular", password="pass")
        client.force_login(user)

        response = client.get("/submissions/")

        assertRedirects(response, "/no-access/", target_status_code=403)

    def test_submissions_basic_sanity_check(self, admin_client):
        """
        This test won't work without data, because it's running group_by and
        requires non-empty dataframe
        """
        PretalxData.objects.create(
            resource=PretalxData.PretalxResources.submissions,
            content=[
                {
                    "code": "ABCDEF",
                    "slot": None,
                    "tags": [],
                    "image": None,
                    "notes": "",
                    "state": "submitted",
                    "title": "Title",
                    "track": {"en": "Machine Learning, NLP and CV"},
                    "created": "2025-01-14T01:24:36.328974+01:00",
                    "answers": [],
                    "tag_ids": [],
                    "abstract": "Abstract",
                    "duration": 30,
                    "speakers": [],
                    "submission_type": "Talk",
                },
                {
                    "code": "XYZF12",
                    "slot": None,
                    "tags": [],
                    "image": None,
                    "notes": "Notes",
                    "state": "withdrawn",
                    "title": "Title 2",
                    "track": {"en": "Track 2"},
                    "answers": [],
                    "created": "2025-01-16T11:44:26.328974+01:00",
                    "tag_ids": [],
                    "abstract": "Minimal Abstract",
                    "duration": 45,
                    "speakers": [],
                    "submission_type": {"en": "Talk (long session)"},
                },
            ],
        )

        response = admin_client.get("/submissions/")

        assert response.status_code == 200
        assertTemplateUsed(response, "submissions.html")
