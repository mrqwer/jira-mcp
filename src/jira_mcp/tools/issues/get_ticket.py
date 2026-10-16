from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp

DEFAULT_ISSUE_FIELDS = [
    "summary",
    "description",
    "status",
    "assignee",
    "reporter",
    "issuetype",
    "priority",
    "labels",
    "components",
    "fixVersions",
    "parent",
    "subtasks",
    "created",
    "updated",
    "duedate",
    "comment",
    "issuelinks",
    "attachment",
    "timetracking",
]


@mcp.tool()
def get_ticket(
    issue_key: str,
    fields: list[str] | None = None,
    comment_limit: int = 10,
) -> dict[str, Any]:
    """Get an issue with useful fields, links, attachments, and recent comments."""
    data = client.request(
        "GET",
        client.issue_path(issue_key),
        params={
            "fields": ",".join(fields or DEFAULT_ISSUE_FIELDS),
            "expand": "names,schema",
        },
    )

    comments = data.get("fields", {}).get("comment")
    if comments and "comments" in comments:
        limit = max(0, min(comment_limit, 50))
        comments["comments"] = comments["comments"][-limit:] if limit else []

    data["browse_url"] = client.browse_url(data.get("key", issue_key))
    return data
