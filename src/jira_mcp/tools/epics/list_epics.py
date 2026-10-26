from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def list_epics(
    board_id: int,
    done: bool | None = None,
    start_at: int = 0,
    max_results: int = 20,
) -> dict[str, Any]:
    """List the epics of a board; done=false keeps open epics, done=true finished ones.

    Returns {items, start_at, max_results, total, next_start_at}."""
    page = client.page(
        f"board/{board_id}/epic",
        "values",
        start_at=start_at,
        max_results=max_results,
        params={"done": str(done).lower()} if done is not None else None,
        api="agile",
    )
    page["items"] = [
        {
            "id": epic.get("id"),
            "key": epic.get("key"),
            "name": epic.get("name"),
            "summary": epic.get("summary"),
            "done": epic.get("done"),
            "browse_url": client.browse_url(epic.get("key")),
        }
        for epic in page["items"]
    ]
    return page
