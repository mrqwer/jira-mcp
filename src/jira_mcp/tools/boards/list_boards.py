from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def list_boards(
    project_key: str | None = None,
    board_type: str | None = None,
    name: str | None = None,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """List agile boards, optionally for one project, type ("scrum"/"kanban") or name fragment.

    Returns {items, start_at, max_results, total, next_start_at}."""
    params: dict[str, Any] = {}
    if project_key:
        params["projectKeyOrId"] = project_key
    if board_type:
        params["type"] = board_type
    if name:
        params["name"] = name

    page = client.page(
        "board", "values", start_at=start_at, max_results=max_results, params=params, api="agile"
    )
    page["items"] = [
        {"id": board.get("id"), "name": board.get("name"), "type": board.get("type")}
        for board in page["items"]
    ]
    return page
