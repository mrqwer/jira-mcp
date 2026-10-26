from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.sprints.list_sprints import sprint_summary


@mcp.tool()
def start_sprint(sprint_id: int, start_date: str, end_date: str) -> dict[str, Any]:
    """Start a future sprint. Only one sprint per board can usually be active.

    Dates use ISO 8601 with offset, e.g. "2026-11-02T09:00:00.000+05:00"."""
    sprint = client.request(
        "POST",
        f"sprint/{sprint_id}",
        json={"state": "active", "startDate": start_date, "endDate": end_date},
        api="agile",
    )
    return sprint_summary(sprint)
