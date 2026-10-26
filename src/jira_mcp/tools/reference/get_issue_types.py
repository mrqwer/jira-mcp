from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_issue_types() -> list[dict[str, Any]]:
    """List every issue type in this Jira instance.

    For the types that can be created in one project, use
    get_project_issue_types instead."""
    return [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "subtask": bool(t.get("subtask")),
            "description": t.get("description"),
        }
        for t in client.request("GET", "issuetype")
    ]
