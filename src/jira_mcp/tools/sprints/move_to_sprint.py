from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.formatting import require_issue_keys


@mcp.tool()
def move_to_sprint(sprint_id: int, issue_keys: list[str]) -> dict[str, Any]:
    """Move issues (up to 50) into a future or active sprint."""
    require_issue_keys(issue_keys)
    client.request(
        "POST",
        f"sprint/{sprint_id}/issue",
        expected=(204,),
        json={"issues": issue_keys},
        api="agile",
    )
    return {"sprint_id": sprint_id, "moved": issue_keys}
