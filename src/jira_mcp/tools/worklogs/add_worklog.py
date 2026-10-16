from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def add_worklog(
    issue_key: str,
    time_spent: str,
    comment: str = "",
    started: str | None = None,
) -> dict[str, Any]:
    """Log work such as '1h 30m'. started uses Jira's ISO-like timestamp format."""
    payload: dict[str, Any] = {"timeSpent": time_spent}
    if comment:
        payload["comment"] = comment
    if started:
        payload["started"] = started
    return client.request(
        "POST",
        client.issue_path(issue_key, "/worklog"),
        expected=(201,),
        json=payload,
    )
