from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def remove_watcher(issue_key: str, username: str) -> dict[str, Any]:
    """Remove a user (Jira username) from an issue's watchers."""
    client.request(
        "DELETE",
        client.issue_path(issue_key, "/watchers"),
        expected=(204,),
        params={"username": username},
    )
    return {"key": issue_key, "removed_watcher": username}
