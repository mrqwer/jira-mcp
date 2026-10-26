from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_worklogs(
    issue_key: str,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """Read the work logged on an issue page by page.

    Returns {items, start_at, max_results, total, next_start_at}; pass
    next_start_at as start_at for the next page (null on the last page)."""
    page = client.page(
        client.issue_path(issue_key, "/worklog"),
        "worklogs",
        start_at=start_at,
        max_results=max_results,
    )
    page["items"] = [
        {
            "id": worklog.get("id"),
            "author": (worklog.get("author") or {}).get("displayName"),
            "author_username": (worklog.get("author") or {}).get("name"),
            "started": worklog.get("started"),
            "time_spent": worklog.get("timeSpent"),
            "time_spent_seconds": worklog.get("timeSpentSeconds"),
            "comment": worklog.get("comment"),
        }
        for worklog in page["items"]
    ]
    return page
