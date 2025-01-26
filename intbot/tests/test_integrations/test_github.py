import pytest
from core.integrations.github import (
    GithubProjectV2Item,
    GithubSender,
    parse_github_webhook,
)
from core.models import Webhook
from httpx import Response


def test_parse_github_webhook_raises_value_error_for_unsupported():
    headers = {"X-Github-Event": "random_event"}
    wh = Webhook(meta=headers, content={}, extra={})

    with pytest.raises(ValueError):
        parse_github_webhook(wh)


def test_github_project_created_event():
    parser = GithubProjectV2Item(
        action="created",
        headers={},
        content={
            "sender": {"login": "testuser", "html_url": "https://github.com/testuser"},
            "projects_v2_item": {
                "content_type": "Issue",
                "node_id": "test_node_id",
            },
            "action": "created",
        },
        extra={
            "content": {
                "__typename": "Issue",
                "id": "I_randomIssueID",
                "title": "Test Issue",
                "url": "https://github.com/test-issue",
            }
        },
    )

    message = parser.as_discord_message()

    assert message == (
        "[@testuser](https://github.com/testuser) created "
        "[Test Issue](https://github.com/test-issue)"
    )


def test_github_project_edited_event_for_status_change():
    parser = GithubProjectV2Item(
        action="changed",
        headers={},
        content={
            "sender": {"login": "testuser", "html_url": "https://github.com/testuser"},
            "projects_v2_item": {
                "content_type": "Issue",
                "node_id": "test_node_id",
            },
            "action": "edited",
            "changes": {
                "field_value": {
                    "field_name": "Status",
                    "field_type": "single_select",
                    "from": {"name": "To Do"},
                    "to": {"name": "In Progress"},
                }
            },
        },
        extra={
            "content": {
                "__typename": "Issue",
                "id": "I_randomIssueID",
                "title": "Test Issue",
                "url": "https://github.com/test-issue",
            }
        },
    )

    message = parser.as_discord_message()

    assert message == (
        "[@testuser](https://github.com/testuser) changed **Status** of "
        "**[Test Issue](https://github.com/test-issue)** "
        "from **To Do** to **In Progress**"
    )


def test_github_project_edited_event_for_date_change():
    parser = GithubProjectV2Item(
        action="edited",
        headers={},
        content={
            "sender": {"login": "testuser", "html_url": "https://github.com/testuser"},
            "projects_v2_item": {
                "content_type": "Issue",
                "node_id": "test_node_id",
            },
            "action": "edited",
            "changes": {
                "field_value": {
                    "field_name": "Deadline",
                    "field_type": "date",
                    "from": "2024-01-01T10:20:30",
                    "to": "2025-01-05T20:30:10",
                }
            },
        },
        extra={
            "content": {
                "__typename": "Issue",
                "id": "I_randomIssueID",
                "title": "Test Issue",
                "url": "https://github.com/test-issue",
            }
        },
    )

    message = parser.as_discord_message()

    assert message == (
        "[@testuser](https://github.com/testuser) edited **Deadline** of "
        "**[Test Issue](https://github.com/test-issue)** "
        "from **2024-01-01** to **2025-01-05**"
    )


def test_github_project_item_draft_issue_created():
    parser = GithubProjectV2Item(
        action="created",
        headers={},
        content={
            "sender": {"login": "testuser", "html_url": "https://github.com/testuser"},
            "projects_v2_item": {},
            "action": "created",
        },
        extra={
            "content": {
                "__typename": "DraftIssue",
                "id": "DI_randomDraftIssueID",
                "title": "Draft Title",
            }
        },
    )

    message = parser.as_discord_message()

    assert message == "[@testuser](https://github.com/testuser) created Draft Title"


def test_github_project_item_edited_event_no_changes():
    parser = GithubProjectV2Item(
        action="edited",
        headers={},
        content={
            "sender": {"login": "testuser", "html_url": "https://github.com/testuser"},
            "projects_v2_item": {},
            "action": "edited",
        },
        extra={
            "content": {
                "__typename": "Issue",
                "id": "I_randomIssueID",
                "title": "Test Issue",
                "url": "https://github.com/test-issue",
            }
        },
    )

    message = parser.as_discord_message()

    assert message == (
        "[@testuser](https://github.com/testuser) edited "
        "[Test Issue](https://github.com/test-issue)"
    )


class TestGithubProjectV2ItemSpecial:
    def test_get_project_parses_project_correctly(self, gh_data):
        wh = Webhook(
            meta={"X-Github-Event": "projects_v2_item"},
            content=gh_data["project_v2_item.edited"],
            extra=gh_data["query_result"],
        )
        gwh = parse_github_webhook(wh)

        ghp = gwh.get_project()

        assert ghp.title == "Board Project"
        assert ghp.url == "https://github.com/orgs/EuroPython/projects/1337"

    def test_get_sender_parses_sender_correctly(self, gh_data):
        wh = Webhook(
            meta={"X-Github-Event": "projects_v2_item"},
            content=gh_data["project_v2_item.edited"],
            extra=gh_data["query_result"],
        )
        gwh = parse_github_webhook(wh)

        sender = gwh.get_sender()

        assert isinstance(sender, GithubSender)
        assert sender.login == "github-project-automation[bot]"
        assert sender.html_url == "https://github.com/apps/github-project-automation"

    def test_sender_formats_sender_correctly(self, gh_data):
        wh = Webhook(
            meta={"X-Github-Event": "projects_v2_item"},
            content=gh_data["project_v2_item.edited"],
            extra=gh_data["query_result"],
        )
        gwh = parse_github_webhook(wh)

        sender = gwh.sender()

        assert isinstance(sender, str)
        assert (
            sender == "[@github-project-automation[bot]]("
            "https://github.com/apps/github-project-automation"
            ")"
        )
