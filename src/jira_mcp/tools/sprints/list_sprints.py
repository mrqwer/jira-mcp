from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


def sprint_summary(sprint: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": sprint.get("id"),
        "name": sprint.get("name"),
        "state": sprint.get("state"),
        "start_date": sprint.get("startDate"),
        "end_date": sprint.get("endDate"),
        "complete_date": sprint.get("completeDate"),
        "goal": sprint.get("goal"),
    }


@mcp.tool()
def list_sprints(
    board_id: int,
    state: str | None = None,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """List a scrum board's sprints; state filters by "future", "active", "closed" (comma-separated).

    Kanban boards have no sprints; Jira rejects the call for them.
    Returns {items, start_at, max_results, total, next_start_at}."""
    page = client.page(
        f"board/{board_id}/sprint",
        "values",
        start_at=start_at,
        max_results=max_results,
        params={"state": state} if state else None,
        api="agile",
    )
    page["items"] = [sprint_summary(sprint) for sprint in page["items"]]
    return page
