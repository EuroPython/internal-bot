import logging

import pytest
from core.models import DiscordMessage, Webhook
from core.tasks import process_github_webhook, process_internal_webhook, process_webhook
from django_tasks.task import ResultStatus


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
