from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def list_transitions(issue_key: str) -> list[dict[str, Any]]:
    """List workflow transitions currently available for an issue."""
    data = client.request(
        "GET",
        client.issue_path(issue_key, "/transitions"),
        params={"expand": "transitions.fields"},
    )
    return data.get("transitions", [])
