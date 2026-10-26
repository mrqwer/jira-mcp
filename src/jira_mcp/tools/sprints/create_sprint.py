from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.sprints.list_sprints import sprint_summary


@mcp.tool()
def create_sprint(
    board_id: int,
    name: str,
    goal: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Create a future sprint on a scrum board.

    Dates use ISO 8601 with offset, e.g. "2026-11-02T09:00:00.000+05:00"."""
    payload: dict[str, Any] = {"name": name, "originBoardId": board_id}
    if goal:
        payload["goal"] = goal
    if start_date:
        payload["startDate"] = start_date
    if end_date:
        payload["endDate"] = end_date

    sprint = client.request("POST", "sprint", expected=(200, 201), json=payload, api="agile")
    return sprint_summary(sprint)
