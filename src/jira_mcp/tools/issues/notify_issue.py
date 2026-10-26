from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def notify_issue(
    issue_key: str,
    subject: str,
    text: str,
    usernames: list[str] | None = None,
    reporter: bool = False,
    assignee: bool = False,
    watchers: bool = False,
) -> dict[str, Any]:
    """Send an email notification about an issue to chosen users and/or its reporter, assignee, watchers.

    Requires outgoing mail to be configured in Jira."""
    if not (usernames or reporter or assignee or watchers):
        raise ValueError("Pass usernames or set reporter, assignee or watchers")

    client.request(
        "POST",
        client.issue_path(issue_key, "/notify"),
        expected=(204,),
        json={
            "subject": subject,
            "textBody": text,
            "to": {
                "reporter": reporter,
                "assignee": assignee,
                "watchers": watchers,
                "users": [{"name": name} for name in usernames or []],
            },
        },
    )
    return {"key": issue_key, "notified": True}
