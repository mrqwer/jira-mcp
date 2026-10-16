from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def assign_ticket(
    issue_key: str,
    assignee_username: str | None,
) -> dict[str, Any]:
    """Assign an issue by Jira username. Pass null to unassign it."""
    client.request(
        "PUT",
        client.issue_path(issue_key, "/assignee"),
        expected=(204,),
        json={"name": assignee_username},
    )
    return {"key": issue_key, "assignee": assignee_username}
