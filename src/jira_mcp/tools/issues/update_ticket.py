from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def update_ticket(
    issue_key: str,
    fields: dict[str, Any],
    notify_users: bool = True,
) -> dict[str, Any]:
    """Update Jira issue fields using the same field shapes returned by metadata."""
    client.request(
        "PUT",
        client.issue_path(issue_key),
        expected=(204,),
        params={"notifyUsers": str(notify_users).lower()},
        json={"fields": fields},
    )
    return {"key": issue_key, "updated_fields": sorted(fields)}
