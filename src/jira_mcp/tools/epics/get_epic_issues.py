from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp.app import mcp
from jira_mcp.formatting import issue_page


@mcp.tool()
def get_epic_issues(
    epic_key: str,
    jql: str | None = None,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """List the issues that belong to an epic (by epic key or id), optionally narrowed with JQL.

    Returns {items, start_at, max_results, total, next_start_at}."""
    return issue_page(
        f"epic/{quote(str(epic_key), safe='')}/issue",
        jql=jql,
        start_at=start_at,
        max_results=max_results,
    )
