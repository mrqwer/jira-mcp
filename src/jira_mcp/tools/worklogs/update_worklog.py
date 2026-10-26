from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def update_worklog(
    issue_key: str,
    worklog_id: str,
    time_spent: str | None = None,
    comment: str | None = None,
    started: str | None = None,
) -> dict[str, Any]:
    """Change a worklog's time spent (e.g. "2h"), comment or start time. Get ids from get_worklogs."""
    payload: dict[str, Any] = {}
    if time_spent:
        payload["timeSpent"] = time_spent
    if comment is not None:
        payload["comment"] = comment
    if started:
        payload["started"] = started
    if not payload:
        raise ValueError("Pass time_spent, comment or started")

    return client.request(
        "PUT",
        client.issue_path(issue_key, f"/worklog/{quote(str(worklog_id), safe='')}"),
        json=payload,
    )
