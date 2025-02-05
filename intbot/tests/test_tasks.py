import logging
from django.conf import settings

import pytest
import respx
from core.integrations.github import GITHUB_API_URL
from core.models import DiscordMessage, Webhook
from core.tasks import process_github_webhook, process_internal_webhook, process_webhook
from django.utils import timezone
from django_tasks.task import ResultStatus
from httpx import Response


@pytest.mark.django_db
def test_process_internal_webhook_handles_internal_webhook_correctly():
    wh = Webhook.objects.create(
        source="internal",
        event="test1",
        content={
            "random": "content",
        },
        extra={},
    )

    process_internal_webhook(wh)

    dm = DiscordMessage.objects.get()
    assert dm.content == "Webhook content: {'random': 'content'}"
    assert dm.channel_id == "12345"
    assert dm.channel_name == "#test-channel"


@pytest.mark.django_db
def test_process_internal_webhook_fails_if_incorrect_source():
    wh = Webhook(source="asdf")

    with pytest.raises(ValueError):
        process_internal_webhook(wh)


@pytest.mark.django_db
def test_process_webhook_fails_if_unsupported_source():
    wh = Webhook.objects.create(
        source="asdf",
        event="test1",
        content={},
        extra={},
    )

    # If the task is enqueued the errors are not emited.
    # Instead we have to check the result
    result = process_webhook.enqueue(str(wh.uuid))

    assert result.status == ResultStatus.FAILED
    assert result.traceback.endswith("ValueError: Unsupported source asdf\n")


@pytest.mark.django_db
def test_process_github_webhook_logs_unsupported_event(caplog):
    wh = Webhook.objects.create(
        source="github",
        event="",
        meta={"X-Github-Event": "testrandom"},
        content={},
        extra={},
    )

    with caplog.at_level(logging.INFO):
        process_github_webhook(wh)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert (
        caplog.records[0].message
        == f"Not processing Github Webhook {wh.uuid}: Event `testrandom` not supported"
    )


@pytest.mark.django_db
@respx.mock
def test_process_github_webhook_skips_a_message_when_unsupported_project(
    github_data,
):
    wh = Webhook.objects.create(
        source="github",
        event="",
        meta={"X-Github-Event": "projects_v2_item"},
        content=github_data["project_v2_item.edited"],
        extra={},
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
    process_github_webhook(wh)

    # Skip the message but mark as processed
    assert DiscordMessage.objects.count() == 0
    assert wh.processed_at is not None
    assert wh.processed_at < timezone.now()
    assert wh.event == "projects_v2_item.edited"


@pytest.mark.django_db
@respx.mock
def test_process_github_webhook_creates_a_message_from_supported(
    github_data,
):
    wh = Webhook.objects.create(
        source="github",
        event="",
        meta={"X-Github-Event": "projects_v2_item"},
        content=github_data["project_v2_item.edited"],
        extra={},
    )
    node = {
        "project": {
            "id": "PVT_Test_Board_Project",
            "title": "Test Board Project",
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
    process_github_webhook(wh)

    dm = DiscordMessage.objects.get()
    assert wh.processed_at is not None
    assert wh.processed_at < timezone.now()
    assert wh.event == "projects_v2_item.edited"
    assert dm.channel_id == settings.DISCORD_BOARD_CHANNEL_ID
    assert dm.channel_name == settings.DISCORD_BOARD_CHANNEL_NAME
    assert dm.content == (
        "GitHub: [@github-project-automation[bot]]"
        "(https://github.com/apps/github-project-automation)"
        " projects_v2_item.edited **Status** of "
        "**[Test Issue](https://github.com/test-issue)**"
        " from **Done** to **In progress**"
    )
    assert dm.sent_at is None
