import pytest
import respx
from core.integrations.github import (
    GITHUB_API_URL,
    GithubProjectV2Item,
    fetch_github_item_details,
    parse_github_webhook,
)
from httpx import Response


def test_parse_github_webhook_raises_value_error_for_unsupported():
    headers = {"X-Github-Event": "random_event"}
    content = {}

    with pytest.raises(ValueError):
        parse_github_webhook(headers, content)


@pytest.fixture
def mocked_github_response():
    def _mock_response(item_type, content_data):
        return {"data": {"node": {"content": content_data}}}

    return _mock_response


@pytest.fixture
def sample_content():
    return {
        "sender": {"login": "testuser", "html_url": "https://github.com/testuser"},
        "projects_v2_item": {
            "content_type": "Issue",
            "node_id": "test_node_id",
        },
    }


@respx.mock
def test_fetch_github_item_details(mocked_github_response):
    mocked_response = mocked_github_response(
        "Issue",
        {
            "id": "test_issue_id",
            "title": "Test Issue",
            "url": "https://github.com/test/repo/issues/1",
        },
    )
    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))

    result = fetch_github_item_details("test_node_id")

    assert result["id"] == "test_issue_id"
    assert result["title"] == "Test Issue"
    assert result["url"] == "https://github.com/test/repo/issues/1"


@respx.mock
def test_github_project_created_event(mocked_github_response, sample_content):
    sample_content["action"] = "created"
    mocked_response = mocked_github_response(
        "Issue",
        {
            "id": "test_issue_id",
            "title": "Test Issue",
            "url": "https://github.com/test/repo/issues/1",
        },
    )
    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))

    parser = GithubProjectV2Item(sample_content)
    message = parser.as_str()

    assert message == (
        "[@testuser](https://github.com/testuser) created "
        "[Test Issue](https://github.com/test/repo/issues/1)"
    )


@respx.mock
def test_github_project_edited_event_for_status_change(
    mocked_github_response, sample_content
):
    sample_content["action"] = "edited"
    sample_content["changes"] = {
        "field_value": {
            "field_name": "Status",
            "field_type": "single_select",
            "from": {"name": "To Do"},
            "to": {"name": "In Progress"},
        }
    }
    mocked_response = mocked_github_response(
        "Issue",
        {
            "id": "test_issue_id",
            "title": "Test Issue",
            "url": "https://github.com/test/repo/issues/1",
        },
    )
    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))

    parser = GithubProjectV2Item(sample_content)
    message = parser.as_str()

    assert message == (
        "[@testuser](https://github.com/testuser) changed **Status** of "
        "**[Test Issue](https://github.com/test/repo/issues/1)** "
        "from **To Do** to **In Progress**"
    )


@respx.mock
def test_github_project_edited_event_for_date_change(
    mocked_github_response, sample_content
):
    sample_content["action"] = "edited"
    sample_content["changes"] = {
        "field_value": {
            "field_name": "Deadline",
            "field_type": "date",
            "from": "2024-01-01T10:20:30",
            "to": "2025-01-05T20:30:10",
        }
    }
    mocked_response = mocked_github_response(
        "Issue",
        {
            "id": "test_issue_id",
            "title": "Test Issue",
            "url": "https://github.com/test/repo/issues/1",
        },
    )
    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))

    parser = GithubProjectV2Item(sample_content)
    message = parser.as_str()

    assert message == (
        "[@testuser](https://github.com/testuser) changed **Deadline** of "
        "**[Test Issue](https://github.com/test/repo/issues/1)** "
        "from **2024-01-01** to **2025-01-05**"
    )


@respx.mock
def test_github_project_draft_issue_event(mocked_github_response, sample_content):
    sample_content["action"] = "created"
    sample_content["projects_v2_item"]["content_type"] = "DraftIssue"
    mocked_response = mocked_github_response(
        "DraftIssue",
        {
            "id": "draft_issue_id",
            "title": "Draft Title",
        },
    )
    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))

    parser = GithubProjectV2Item(sample_content)
    message = parser.as_str()

    assert message == "[@testuser](https://github.com/testuser) created Draft Title"


def test_github_project_unsupported_action(sample_content):
    sample_content["action"] = "unsupported_action"

    parser = GithubProjectV2Item(sample_content)

    with pytest.raises(ValueError, match="Action unsupported unsupported_action"):
        parser.action()


@respx.mock
def test_github_project_edited_event_no_changes(mocked_github_response, sample_content):
    sample_content["action"] = "edited"
    mocked_response = mocked_github_response(
        "Issue",
        {
            "id": "test_issue_id",
            "title": "Test Issue",
            "url": "https://github.com/test/repo/issues/1",
        },
    )
    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))

    parser = GithubProjectV2Item(sample_content)
    message = parser.as_str()

    assert message == (
        "[@testuser](https://github.com/testuser) changed "
        "[Test Issue](https://github.com/test/repo/issues/1)"
    )


@respx.mock
def test_fetch_github_item_details_api_error():
    respx.post(GITHUB_API_URL).mock(
        return_value=Response(500, json={"message": "Internal Server Error"})
    )

    with pytest.raises(Exception, match="GitHub API error: 500 - .*"):
        fetch_github_item_details("test_node_id")
