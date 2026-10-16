from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def search_tickets(
    jql_query: str,
    max_results: int = 10,
    start_at: int = 0,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Search Jira with JQL. Results are capped by JIRA_MAX_RESULTS (default 50)."""
    data = client.request(
        "GET",
        "search",
        params={
            "jql": jql_query,
            "startAt": max(0, start_at),
            "maxResults": client.bounded_results(max_results),
            "fields": ",".join(
                fields
                or [
                    "summary",
                    "status",
                    "assignee",
                    "issuetype",
                    "priority",
                    "updated",
                ]
            ),
        },
    )
    for issue in data.get("issues", []):
        issue["browse_url"] = client.browse_url(issue["key"])
    return data
