from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def find_users(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Find Jira users by username, display name, or email fragment."""
    data = client.request(
        "GET",
        "user/picker",
        params={"query": query, "maxResults": client.bounded_results(max_results)},
    )
    return data.get("users", [])
