from __future__ import annotations

from typing import Any

from jira_mcp.app import mcp
from jira_mcp.formatting import issue_page


@mcp.tool()
def get_board_issues(
    board_id: int,
    jql: str | None = None,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """List the issues on a board, optionally narrowed with extra JQL (e.g. "assignee = currentUser()").

    Returns {items, start_at, max_results, total, next_start_at}."""
    return issue_page(
        f"board/{board_id}/issue", jql=jql, start_at=start_at, max_results=max_results
    )
