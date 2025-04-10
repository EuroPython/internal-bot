"""
The Github Integration is mostly about parsing Github Webhooks.

This is split into three parts.

1. Save the webhook in the database (not in this file)
2. Prep webhook - download extra data that's missing in the webhook
3. Proces webhook - usually means create a discord message with a notification
"""

from typing import Any

import httpx
from core.models import Webhook
from django.conf import settings
from pydantic import BaseModel

GITHUB_API_URL = "https://api.github.com/graphql"

# GraphQL query
project_item_details_query = """
query($itemId: ID!) {
  node(id: $itemId) {
    ... on ProjectV2Item {
      id
      project {
          id
          title
          url
      }
      content {
        __typename
        ... on DraftIssue {
          id
          title
        }
        ... on Issue {
          id
          title
          url
        }
      }
    }
  }
}
"""


class GithubRepositories:
    website_repo = ...
    bot_repo = ...


class GithubProjects:
    board_project = settings.GITHUB_BOARD_PROJECT_ID
    ep2025_project = settings.GITHUB_EP2025_PROJECT_ID
    em_project = settings.GITHUB_EM_PROJECT_ID


class GithubProject(BaseModel):
    id: str
    title: str
    url: str


class GithubRepository(BaseModel):
    id: str
    name: str


class GithubSender(BaseModel):
    login: str
    html_url: str


class GithubIssue(BaseModel):
    id: str
    title: str
    url: str

    def as_discord_message(self):
        return f"[{self.title}]({self.url})"


class GithubDraftIssue(BaseModel):
    id: str
    title: str

    def as_discord_message(self):
        return self.title


JsonType = dict[str, Any]


class GithubWebhook:
    """
    Base class for all the other specific types of webhooks.
    """

    def __init__(
        self, action: str, headers: JsonType, content: JsonType, extra: JsonType
    ):
        self.action = action
        self.headers = headers
        self.content = content
        self.extra = extra
        self._project = None
        self._repository = None

    @classmethod
    def from_webhook(cls, wh: Webhook):
        assert wh.extra, "Extra should be set already at this point"
        return cls(
            content=wh.content,
            headers=wh.meta,
            extra=wh.extra,
            action=wh.event,
        )

    def get_project(self):  # pragma: no cover
        """Used in the discord channel router"""
        raise NotImplementedError("Implement in child class")

    def get_repository(self):  # pragma: no cover
        """Used in the discord channel router"""
        raise NotImplementedError("Implement in child class")


class GithubProjectV2Item(GithubWebhook):
    # NOTE: This might be something for pydantic schemas in the future

    def short_action(self):
        # "projects_v2_item.edited" -> changed
        # "projects_v2_item.created" -> created
        action = self.action.split(".")[1]
        return {
            "edited": "changed",
        }.get(action, action)

    @property
    def sender(self):
        sender = self.get_sender()

        return f"[@{sender.login}]({sender.html_url})"

    def get_sender(self) -> GithubSender:
        return GithubSender.model_validate(self.content["sender"])

    def github_object(self) -> GithubDraftIssue | GithubIssue:
        content = self.extra["content"]
        typename = content.pop("__typename")

        if typename == "Issue":
            return GithubIssue.model_validate(content)
        elif typename == "DraftIssue":
            return GithubDraftIssue.model_validate(content)
        else:
            raise ValueError("Other types are not supported")

    def get_project(self) -> GithubProject:
        return GithubProject.model_validate(self.extra["project"])

    def get_repository(self) -> GithubRepository:
        # Not relevant at the moment
        return GithubRepository(name="Placeholder", id="placeholder-repo")

    def changes(self) -> dict:
        # Early return! \o/
        if "changes" not in self.content:
            # Fallback because some webhooks just don't have changes.
            return {}

        fv = self.content["changes"]["field_value"]
        field_name = fv["field_name"]
        field_type = fv["field_type"]

        changed_from: str
        changed_to: str

        if field_type == "date":
            changed_from = (
                fv["from"].split("T")[0] if fv["from"] is not None else "None"
            )
            changed_to = fv["to"].split("T")[0] if fv["to"] is not None else "None"

        elif field_type == "single_select":
            changed_from = fv["from"]["name"] if fv["from"] is not None else "None"
            changed_to = fv["to"]["name"] if fv["to"] is not None else "None"

        else:
            changed_from = "None"
            changed_to = "None"

        return {
            "field": field_name,
            "from": changed_from,
            "to": changed_to,
        }

    def as_discord_message(self) -> str:
        message = "{sender} {action} {details}".format

        changes = self.changes()

        if changes:
            details = "**{field}** of **{obj}** from **{from}** to **{to}**".format(
                **{"obj": self.github_object().as_discord_message(), **changes}
            )

        else:
            details = self.github_object().as_discord_message()

        return message(
            **{
                "sender": self.sender,
                "action": self.short_action(),
                "details": details,
            }
        )


def prep_github_webhook(wh: Webhook):
    """
    Downloads the extra data that is missing in the webhook but needed for processing.
    """
    event = wh.meta["X-Github-Event"]

    if event == "projects_v2_item":
        node_id = wh.content["projects_v2_item"]["node_id"]
        project_item = fetch_github_project_item(node_id)
        wh.event = f"{event}.{wh.content['action']}"
        wh.extra = project_item
        wh.save()
        return wh

    raise ValueError(f"Event `{event}` not supported")


class GithubAPIError(Exception):
    """Custom exception for GithubAPI Errors"""

    pass


# Should we have a separate GithubClient that encapsulates this?
# Or at least a function that runs the request.
def fetch_github_project_item(item_id: str) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {settings.GITHUB_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": project_item_details_query, "variables": {"itemId": item_id}}
    response = httpx.post(GITHUB_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["node"]
    else:
        raise GithubAPIError(
            f"GitHub API error: {response.status_code} - {response.text}"
        )


def parse_github_webhook(wh: Webhook):
    event = wh.meta["X-Github-Event"]
    if not wh.extra:
        raise ValueError(
            "Make sure the webhook is ready for pickup. See prep_github_webhook"
        )

    if event == "projects_v2_item":
        return GithubProjectV2Item.from_webhook(wh)

    raise ValueError(f"Event not supported `{event}`")
