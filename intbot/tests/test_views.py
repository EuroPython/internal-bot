from core.models import PretalxData, PretixData
from pytest_django.asserts import assertRedirects, assertTemplateUsed


def test_days_until_view(client):
    response = client.get("/days-until/")

    assert response.status_code == 200
    assertTemplateUsed(response, "days_until.html")


class TestPorductsView:
    def test_products_view_requires_login(self, client):
        response = client.get("/products/")

        assertRedirects(
            response, "/accounts/login/?next=/products/", target_status_code=404
        )
        assert response.status_code == 302

    def test_products_sanity_check(self, admin_client):
        PretixData.objects.create(
            resource=PretixData.PretixResources.products, content=[]
        )

        response = admin_client.get("/products/")

        assert response.status_code == 200
        assertTemplateUsed(response, "table.html")


class TestSubmissionsView:
    def test_submissions_view_requires_login(self, client):
        response = client.get("/submissions/")

        # 404 because we don't have a user login view yet - we can use admin
        # for that
        assertRedirects(
            response, "/accounts/login/?next=/submissions/", target_status_code=404
        )

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
