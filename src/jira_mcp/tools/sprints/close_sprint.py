from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.sprints.list_sprints import sprint_summary


@mcp.tool()
def close_sprint(sprint_id: int) -> dict[str, Any]:
    """Close an active sprint. Unfinished issues are handled by Jira's usual rules."""
    sprint = client.request(
        "POST", f"sprint/{sprint_id}", json={"state": "closed"}, api="agile"
    )
    return sprint_summary(sprint)
