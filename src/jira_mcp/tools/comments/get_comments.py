from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_comments(
    issue_key: str,
    start_at: int = 0,
    max_results: int = 20,
    newest_first: bool = False,
) -> dict[str, Any]:
    """Read an issue's comments page by page.

    Returns {items, start_at, max_results, total, next_start_at}; pass
    next_start_at as start_at for the next page (null on the last page)."""
    page = client.page(
        client.issue_path(issue_key, "/comment"),
        "comments",
        start_at=start_at,
        max_results=max_results,
        params={"orderBy": "-created" if newest_first else "created"},
    )
    page["items"] = [
        {
            "id": comment.get("id"),
            "author": (comment.get("author") or {}).get("displayName"),
            "author_username": (comment.get("author") or {}).get("name"),
            "created": comment.get("created"),
            "updated": comment.get("updated"),
            "body": comment.get("body"),
        }
        for comment in page["items"]
    ]
    return page
