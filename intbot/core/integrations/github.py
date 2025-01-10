import dataclasses

import httpx
from django.conf import settings

GITHUB_API_URL = "https://api.github.com/graphql"

# GraphQL query
query = """
query($itemId: ID!) {
  node(id: $itemId) {
    ... on ProjectV2Item {
      id
      content {
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


def parse_github_webhook(headers: dict, content: dict) -> tuple[str, str]:
    event = headers["X-Github-Event"]

    if event == "projects_v2_item":
        parser = GithubProjectV2Item(content)
        formatted = parser.as_str()
        action = parser.action()
        event_action = f"{event}.{action}"
        return formatted, event_action

    elif event == "...":
        return "", ""

    else:
        raise ValueError(f"Event `{event}` not supported")


@dataclasses.dataclass
class GithubIssue:
    id: str
    title: str
    url: str

    def as_discord_message(self):
        return f"[{self.title}]({self.url})"


@dataclasses.dataclass
class GithubDraftIssue:
    id: str
    title: str

    def as_discord_message(self):
        return self.title


def fetch_github_item_details(item_id):
    headers = {
        "Authorization": f"Bearer {settings.GITHUB_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": query, "variables": {"itemId": item_id}}
    response = httpx.post(GITHUB_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]["node"]["content"]
    else:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")


CONTENT_TYPE_MAP = {
    "Issue": GithubIssue,
    "DraftIssue": GithubDraftIssue,
}


class GithubProjectV2Item:
    def __init__(self, content: dict):
        self.content = content

    def action(self):
        if self.content["action"] == "edited":
            action = "changed"
        elif self.content["action"] == "created":
            action = "created"
        else:
            raise ValueError(f"Action unsupported {self.content['action']}")

        return action

    def sender(self):
        login = self.content["sender"]["login"]
        url = self.content["sender"]["html_url"]

        return f"[@{login}]({url})"

    def content_type(self):
        return self.content["projects_v2_item"]["content_type"]

    def node_id(self):
        # NOTE(artcz): This is more relevant, because of how the graphql query
        # above is constructed.
        # Using node_id, which is an id of a ProjectV2Item we can get both
        # DraftIssue and Issue from one query.
        # If we use the content_node_id we need to adjust the query as that ID
        # points us directly either an Issue or DraftIssue
        return self.content["projects_v2_item"]["node_id"]

    def content_node_id(self):
        return self.content["projects_v2_item"]["content_node_id"]

    def changes(self) -> dict:
        if "changes" in self.content:
            fv = self.content["changes"]["field_value"]
            field_name = fv["field_name"]
            field_type = fv["field_type"]
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

        return {}

    def as_discord_message(self, github_object: GithubDraftIssue | GithubIssue) -> str:
        message = "{sender} {action} {details}".format

        action = self.action()
        sender = self.sender()

        changes = self.changes()

        if changes:
            details = "**{field}** of **{obj}** from **{from}** to **{to}**".format
            details = details(**{"obj": github_object.as_discord_message(), **changes})

        else:
            details = github_object.as_discord_message()

        return message(
            **{
                "sender": sender,
                "action": action,
                "details": details,
            }
        )

    def fetch_quoted_github_object(self) -> GithubIssue | GithubDraftIssue:
        obj = fetch_github_item_details(self.node_id())

        obj = CONTENT_TYPE_MAP[self.content_type()](**obj)

        return obj

    def as_str(self):
        github_obj = self.fetch_quoted_github_object()
        return self.as_discord_message(github_obj)
