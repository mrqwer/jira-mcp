from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def list_favourite_filters() -> list[dict[str, Any]]:
    """List the authenticated user's favourite (starred) saved filters with their JQL."""
    return [
        {
            "id": f.get("id"),
            "name": f.get("name"),
            "jql": f.get("jql"),
            "owner": (f.get("owner") or {}).get("name"),
            "description": f.get("description"),
        }
        for f in client.request("GET", "filter/favourite")
    ]
