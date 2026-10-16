from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def create_ticket(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    assignee_username: str | None = None,
    parent_key: str | None = None,
    labels: list[str] | None = None,
    priority: str | None = None,
    additional_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an issue. Use get_create_fields before sending project custom fields."""
    fields = dict(additional_fields or {})
    fields.update(
        {
            "project": {"key": project_key.upper()},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
    )
    if assignee_username:
        fields["assignee"] = {"name": assignee_username}
    if parent_key:
        fields["parent"] = {"key": parent_key}
    if labels is not None:
        fields["labels"] = labels
    if priority:
        fields["priority"] = {"name": priority}

    data = client.request("POST", "issue", expected=(201,), json={"fields": fields})
    data["browse_url"] = client.browse_url(data["key"])
    return data
