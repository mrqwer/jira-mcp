from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.formatting import require_issue_keys


@mcp.tool()
def move_to_backlog(issue_keys: list[str]) -> dict[str, Any]:
    """Move issues (up to 50) out of their sprints into the backlog."""
    require_issue_keys(issue_keys)
    client.request(
        "POST", "backlog/issue", expected=(204,), json={"issues": issue_keys}, api="agile"
    )
    return {"moved_to_backlog": issue_keys}
