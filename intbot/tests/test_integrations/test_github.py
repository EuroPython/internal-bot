import pytest
import respx
from core.integrations.github import (
    GITHUB_API_URL,
    GithubProjectV2Item,
    GithubAPIError,
    GithubSender,
    parse_github_webhook,
    prep_github_webhook,
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


class TestGithubProjectV2Item:

    def test_changes_for_single_select(self):
        parser = GithubProjectV2Item(
            action="changed",
            headers={},
            content={
                "changes": {
                    "field_value": {
                        "field_name": "Status",
                        "field_type": "single_select",
                        "from": {"name": "To Do"},
                        "to": {"name": "In Progress"},
                    }
                },
            },
            extra={},
        )

        assert parser.changes() == {
            "from": "To Do",
            "to": "In Progress",
            "field": "Status",
        }

    def test_changes_for_date(self):
        parser = GithubProjectV2Item(
            action="changed",
            headers={},
            content={
                "changes": {
                    "field_value": {
                        "field_name": "Deadline",
                        "field_type": "date",
                        "from": "2024-01-01T10:20:30",
                        "to": "2025-01-05T20:30:10",
                    }
                },
            },
            extra={},
        )

        assert parser.changes() == {
            "from": "2024-01-01",
            "to": "2025-01-05",
            "field": "Deadline",
        }

    def test_changes_for_unsupported_format(self):
        parser = GithubProjectV2Item(
            action="changed",
            headers={},
            content={
                "changes": {
                    "field_value": {
                        "field_name": "Randomfield",
                        "field_type": "unsupported",
                        "from": "This",
                        "to": "That",
                    }
                },
            },
            extra={},
        )

        assert parser.changes() == {
            "from": "None",
            "to": "None",
            "field": "Randomfield",
        }


    def test_get_project_parses_project_correctly(self, github_data):
        wh = Webhook(
            meta={"X-Github-Event": "projects_v2_item"},
            content=github_data["project_v2_item.edited"],
            extra=github_data["query_result"],
        )
        gwh = parse_github_webhook(wh)

        ghp = gwh.get_project()

        assert ghp.title == "Board Project"
        assert ghp.url == "https://github.com/orgs/EuroPython/projects/1337"

    def test_get_sender_parses_sender_correctly(self, github_data):
        wh = Webhook(
            meta={"X-Github-Event": "projects_v2_item"},
            content=github_data["project_v2_item.edited"],
            extra=github_data["query_result"],
        )
        gwh = parse_github_webhook(wh)

        sender = gwh.get_sender()

        assert isinstance(sender, GithubSender)
        assert sender.login == "github-project-automation[bot]"
        assert sender.html_url == "https://github.com/apps/github-project-automation"

    def test_sender_formats_sender_correctly(self, github_data):
        wh = Webhook(
            meta={"X-Github-Event": "projects_v2_item"},
            content=github_data["project_v2_item.edited"],
            extra=github_data["query_result"],
        )
        gwh = parse_github_webhook(wh)


        assert isinstance(gwh.sender, str)
        assert (
            gwh.sender == "[@github-project-automation[bot]]("
            "https://github.com/apps/github-project-automation"
            ")"
        )


def test_prep_github_webhook_fails_if_event_not_supported():
    wh = Webhook(meta={"X-Github-Event": "issue.fixed"})

    with pytest.raises(ValueError):
        prep_github_webhook(wh)


@respx.mock
@pytest.mark.django_db
def test_prep_github_webhook_fetches_extra_data_for_project_v2_item():
    wh = Webhook(
        meta={"X-Github-Event": "projects_v2_item"},
        content={
            "projects_v2_item": {
                "node_id": "PVTI_random_projectItemV2ID",
                "action": "random",
            }
        },
    )
    node = {
        "project": {
            "id": "PVT_Random_Project",
            "title": "Random Project",
            "url": "https://github.com/europython",
        },
        "content": {
            "__typename": "Issue",
            "id": "I_randomIssueID",
            "title": "Test Issue",
            "url": "https://github.com/test-issue",
        },
    }

    mocked_response = {
        "data": {
            "node": node,
        }
    }

    respx.post(GITHUB_API_URL).mock(return_value=Response(200, json=mocked_response))
    wh = prep_github_webhook(wh)

    assert wh.event == "projects_v2_item.random"
    assert wh.extra == node


@respx.mock
def test_prep_github_webhook_reraises_exception_in_case_of_API_error():
    wh = Webhook(
        meta={"X-Github-Event": "projects_v2_item"},
        content={
            "projects_v2_item": {
                "node_id": "PVTI_random_projectItemV2ID",
                "action": "random",
            }
        },
    )

    respx.post(GITHUB_API_URL).mock(return_value=Response(500, json={"lol": "failed"}))

    with pytest.raises(GithubAPIError, match='GitHub API error: 500 - {"lol":"failed"}'):
        wh = prep_github_webhook(wh)


def test_parse_github_webhook_raises_exception_for_unsupported_events():
    wh = Webhook(
        meta={"X-Github-Event": "long_form_content"},
        content={},
        extra={"something": "extra"},
    )

    with pytest.raises(ValueError, match="Event not supported `long_form_content`"):
        parse_github_webhook(wh)
