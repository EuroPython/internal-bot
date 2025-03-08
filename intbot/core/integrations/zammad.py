from datetime import datetime
from django.conf import settings

from core.models import Webhook
from pydantic import BaseModel


class ZammadGroups:
    billing = settings.ZAMMAD_GROUP_BILLING
    helpdesk = settings.ZAMMAD_GROUP_HELPDESK


class ZammadGroup(BaseModel):
    id: int
    name: str


class ZammadUser(BaseModel):
    firstname: str
    lastname: str


class ZammadTicket(BaseModel):
    id: int
    group: ZammadGroup
    title: str
    owner: ZammadUser
    state: str
    number: str
    customer: ZammadUser
    created_at: datetime
    updated_at: datetime
    updated_by: ZammadUser
    article_ids: list[int]


class ZammadArticle(BaseModel):
    sender: str
    internal: bool
    ticket_id: int
    created_at: datetime
    created_by: ZammadUser
    subject: str


class ZammadWebhook(BaseModel):
    ticket: ZammadTicket
    article: ZammadArticle | None


JsonType = dict[str, str | int | float | list | dict]


class ZammadParser:

    class Actions:
        new_ticket_created = "new_ticket_created"
        new_message_in_thread = "new_message_in_thread"
        replied_in_thread = "replied_in_thread"
        new_internal_note = "new_internal_note"
        updated_ticket = "updated_ticket"

    def __init__(self, content: JsonType):
        self.content = content
        # Ticket is always there, article is optional
        # Example: change of status of the Ticket doesn't contain article
        self.ticket = ZammadTicket.model_validate(self.content["ticket"])
        self.article = (
            ZammadArticle.model_validate(self.content["article"])
            if self.content["article"]
            else None
        )

    @property
    def action(self):
        """
        Zammad doesn't give us an action inside the webhook, so we can either
        set custom triggers and URLs for every action, or we can try to infer
        the action from the content of the webhook. For simplcity of the
        overall setup, we are implementing the latter here.

        "New Ticket created"?                -- has article, and len(article_ids) == 1
            -- state change will not have article associated with it.
        "New message in the thread"          -- article, sender==Customer
        "We sent a new reply in the thread"  -- article, sender==Agent
        "New internal note in the thread"    -- article, internal==true
        "Updated the ticket ...",            -- updated_by.firstname
        """
        # Implementing this as cascading if statements here is part of the
        # assumptions.
        # For example the "sender == Customer" is going to be True also for their
        # first message that originally creates the ticket. However first time
        # we get a message, we will return "New ticket" and second time "New
        # message in the thread".
        if self.article and len(self.ticket.article_ids) == 1:
            # This means we have an article, and it's a first one, therefore a
            # ticket is new.
            return self.Actions.new_ticket_created

        elif self.article and self.article.internal is True:
            return self.Actions.new_internal_note

        elif self.article and self.article.sender == "Customer":
            return self.Actions.new_message_in_thread

        elif self.article and self.article.sender == "Agent":
            return self.Actions.replied_in_thread

        elif not self.article:
            return self.Actions.updated_ticket

        raise ValueError("Unsupported scenario")

    @property
    def updated_by(self):
        return self.ticket.updated_by.firstname

    @property
    def group(self):
        return self.ticket.group.name

    @property
    def url(self):
        return f"https://servicedesk.europython.eu/#ticket/zoom/{self.ticket.id}"

    def to_discord_message(self):
        message = "{group}: {sender} {action} {details}".format

        # Action
        actions = {
            self.Actions.new_ticket_created: "created new ticket",
            self.Actions.new_message_in_thread: "sent a new message",
            self.Actions.replied_in_thread: "replied to a ticket",
            self.Actions.new_internal_note: "created internal note",
            self.Actions.updated_ticket: "updated ticket",
        }

        action = actions[self.action]

        return message(group=self.group, sender=self.updated_by, action=action, details=self.url)

    def meta(self):
        return {
            "group": self.group,
            "sender": self.updated_by,
            "action": self.action,
            "message": self.to_discord_message(),
        }


def prep_zammad_webhook(wh: Webhook):
    """Parse and store some information for later"""
    zp = ZammadParser(wh.content)

    wh.event = zp.action
    wh.extra = zp.meta()

    wh.save()

    return wh
