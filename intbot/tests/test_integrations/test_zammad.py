
import pytest
from core.integrations.zammad import ZammadParser, prep_zammad_webhook
from core.models import Webhook
from django.utils import timezone


def test_zammad_parser_with_new_ticket():
    js = {
        "ticket": {
            "id": 123,
            "group": {"id": "123", "name": "TestHelpdesk"},
            "updated_by": {"firstname": "Cookie", "lastname": "Monster"},
            "title": "Test Ticket Title",
            "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
            "state": "open",
            "number": "13374321",
            "customer": {"firstname": "Cookie", "lastname": "Monster"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "article_ids": [1],
        },
        "article": {
            "sender": "Customer",
            "internal": False,
            "ticket_id": 123,
            "created_at": timezone.now(),
            "created_by": {"firstname": "Cookie", "lastname": "Monster"},
            "subject": "New Cookies please",
        },
    }

    zp = ZammadParser(js)

    assert zp.meta() == {
        "group": "TestHelpdesk",
        "sender": "Cookie",
        "action": "new_ticket_created",
        "message": (
            "TestHelpdesk: Cookie created new ticket "
            "https://servicedesk.europython.eu/#ticket/zoom/123"
        ),
    }


def test_zammad_parser_with_new_message():
    js = {
        "ticket": {
            "id": 123,
            "group": {"id": "123", "name": "TestHelpdesk"},
            "updated_by": {"firstname": "Cookie", "lastname": "Monster"},
            "title": "Test Ticket Title",
            "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
            "state": "open",
            "number": "13374321",
            "customer": {"firstname": "Cookie", "lastname": "Monster"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "article_ids": [1, 2],
        },
        "article": {
            "sender": "Customer",
            "internal": False,
            "ticket_id": 123,
            "created_at": timezone.now(),
            "created_by": {"firstname": "Cookie", "lastname": "Monster"},
            "subject": "New Cookies please",
        },
    }

    zp = ZammadParser(js)

    assert zp.meta() == {
        "group": "TestHelpdesk",
        "sender": "Cookie",
        "action": "new_message_in_thread",
        "message": (
            "TestHelpdesk: Cookie sent a new message "
            "https://servicedesk.europython.eu/#ticket/zoom/123"
        ),
    }


def test_zammad_replied_to_a_ticket():
    js = {
        "ticket": {
            "id": 123,
            "group": {"id": "123", "name": "TestHelpdesk"},
            "updated_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "title": "Test Ticket Title",
            "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
            "state": "open",
            "number": "13374321",
            "customer": {"firstname": "Cookie", "lastname": "Monster"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "article_ids": [1, 2],
        },
        "article": {
            "sender": "Agent",
            "internal": False,
            "ticket_id": 123,
            "created_at": timezone.now(),
            "created_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "subject": "New Cookies please",
        },
    }

    zp = ZammadParser(js)

    assert zp.meta() == {
        "group": "TestHelpdesk",
        "sender": "Kermit",
        "action": "replied_in_thread",
        "message": (
            "TestHelpdesk: Kermit replied to a ticket "
            "https://servicedesk.europython.eu/#ticket/zoom/123"
        ),
    }


def test_zammad_create_internal_note():
    js = {
        "ticket": {
            "id": 123,
            "group": {"id": "123", "name": "TestHelpdesk"},
            "updated_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "title": "Test Ticket Title",
            "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
            "state": "open",
            "number": "13374321",
            "customer": {"firstname": "Cookie", "lastname": "Monster"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "article_ids": [1, 2],
        },
        "article": {
            "sender": "Agent",
            "internal": True,
            "ticket_id": 123,
            "created_at": timezone.now(),
            "created_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "subject": "New Cookies please",
        },
    }

    zp = ZammadParser(js)

    assert zp.meta() == {
        "group": "TestHelpdesk",
        "sender": "Kermit",
        "action": "new_internal_note",
        "message": (
            "TestHelpdesk: Kermit created internal note "
            "https://servicedesk.europython.eu/#ticket/zoom/123"
        ),
    }


def test_zammad_updated_ticket():
    js = {
        "ticket": {
            "id": 123,
            "group": {"id": "123", "name": "TestHelpdesk"},
            "updated_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "title": "Test Ticket Title",
            "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
            "state": "closed",
            "number": "13374321",
            "customer": {"firstname": "Cookie", "lastname": "Monster"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "article_ids": [1, 2],
        },
        # No article, just change of status
        "article": {},
    }

    zp = ZammadParser(js)

    assert zp.meta() == {
        "group": "TestHelpdesk",
        "sender": "Kermit",
        "action": "updated_ticket",
        "message": (
            "TestHelpdesk: Kermit updated ticket "
            "https://servicedesk.europython.eu/#ticket/zoom/123"
        ),
    }


def test_zammad_unsupported_scenario():
    """Just for completeness and coverage"""

    js = {
        "ticket": {
            "id": 123,
            "group": {"id": "123", "name": "TestHelpdesk"},
            "updated_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "title": "Test Ticket Title",
            "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
            "state": "closed",
            "number": "13374321",
            "customer": {"firstname": "Cookie", "lastname": "Monster"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "article_ids": [1, 2],
        },
        # No article, just change of status
        "article": {
            "sender": "Unsupported Entity",
            "internal": False,
            "ticket_id": 123,
            "created_at": timezone.now(),
            "created_by": {"firstname": "Kermit", "lastname": "TheFrog"},
            "subject": "New Cookies please",
        },
    }

    zp = ZammadParser(js)

    with pytest.raises(ValueError, match="Unsupported scenario"):
        zp.action


@pytest.mark.django_db
def test_prep_zammad_webhook():
    wh = Webhook.objects.create(
        content={
            "ticket": {
                "id": 123,
                "group": {"id": "123", "name": "TestHelpdesk"},
                "updated_by": {"firstname": "Kermit", "lastname": "TheFrog"},
                "title": "Test Ticket Title",
                "owner": {"firstname": "Kermit", "lastname": "TheFrog"},
                "state": "open",
                "number": "13374321",
                "customer": {"firstname": "Cookie", "lastname": "Monster"},
                "created_at": str(timezone.now()),
                "updated_at": str(timezone.now()),
                "article_ids": [1, 2],
            },
            "article": {
                "sender": "Agent",
                "internal": True,
                "ticket_id": 123,
                "created_at": str(timezone.now()),
                "created_by": {"firstname": "Kermit", "lastname": "TheFrog"},
                "subject": "New Cookies please",
            },
        },
        extra={},
    )

    wh = prep_zammad_webhook(wh)

    assert wh.extra == {
        "group": "TestHelpdesk",
        "sender": "Kermit",
        "action": "new_internal_note",
        "message": (
            "TestHelpdesk: Kermit created internal note "
            "https://servicedesk.europython.eu/#ticket/zoom/123"
        ),
    }
