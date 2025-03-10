import json

import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def github_data():
    """Pytest fixture with examples of webhooks from github"""
    base_path = settings.BASE_DIR / "tests" / "test_integrations" / "github"

    return {
        "project_v2_item.edited": json.load(
            open(base_path / "project_v2_item.edited.json"),
        ),
        "query_result": json.load(
            open(base_path / "query_result.json"),
        )["data"]["node"],
    }
