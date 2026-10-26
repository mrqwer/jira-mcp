from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_watchers(issue_key: str) -> dict[str, Any]:
    """List an issue's watchers and whether the authenticated user is one of them."""
    data = client.request("GET", client.issue_path(issue_key, "/watchers"))
    return {
        "key": issue_key,
        "watch_count": data.get("watchCount", 0),
        "is_watching": data.get("isWatching", False),
        "watchers": [
            {"username": w.get("name"), "display_name": w.get("displayName")}
            for w in data.get("watchers", [])
        ],
    }
