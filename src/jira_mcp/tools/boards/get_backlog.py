from __future__ import annotations

from typing import Any

from jira_mcp.app import mcp
from jira_mcp.formatting import issue_page


@mcp.tool()
def get_backlog(
    board_id: int,
    jql: str | None = None,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """List a scrum board's backlog (issues not in any active or future sprint).

    Kanban boards have no backlog; Jira rejects the call for them.
    Returns {items, start_at, max_results, total, next_start_at}."""
    return issue_page(
        f"board/{board_id}/backlog", jql=jql, start_at=start_at, max_results=max_results
    )
