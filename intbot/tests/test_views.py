from pytest_django.asserts import assertTemplateUsed


def test_days_until_view(client):
    response = client.get("/days-until/")

    assert response.status_code == 200
    assertTemplateUsed(response, "days_until.html")
