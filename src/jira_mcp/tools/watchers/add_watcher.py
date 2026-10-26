from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def add_watcher(issue_key: str, username: str) -> dict[str, Any]:
    """Add a user (Jira username) as a watcher of an issue."""
    client.request(
        "POST", client.issue_path(issue_key, "/watchers"), expected=(204,), json=username
    )
    return {"key": issue_key, "added_watcher": username}
