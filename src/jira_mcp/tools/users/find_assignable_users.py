from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def find_assignable_users(
    project_key: str | None = None,
    issue_key: str | None = None,
    query: str = "",
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """List users who can be assigned issues in a project or on a specific issue.

    Pass project_key (e.g. for a new issue) or issue_key. query filters by a
    username, name or email fragment. Use the returned username with
    assign_ticket or create_ticket."""
    if not project_key and not issue_key:
        raise ValueError("Pass project_key or issue_key")

    params: dict[str, Any] = {
        "username": query,
        "maxResults": client.bounded_results(max_results),
    }
    if issue_key:
        params["issueKey"] = issue_key
    else:
        params["project"] = project_key

    users = client.request("GET", "user/assignable/search", params=params)
    return [
        {
            "username": user.get("name"),
            "display_name": user.get("displayName"),
            "email": user.get("emailAddress"),
            "active": user.get("active"),
        }
        for user in users
    ]
