from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def link_tickets(
    inward_issue_key: str,
    outward_issue_key: str,
    link_type: str,
    comment: str | None = None,
) -> dict[str, Any]:
    """Create a typed relationship between two Jira issues."""
    payload: dict[str, Any] = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue_key},
        "outwardIssue": {"key": outward_issue_key},
    }
    if comment:
        payload["comment"] = {"body": comment}
    client.request("POST", "issueLink", expected=(201,), json=payload)
    return {
        "inward_issue": inward_issue_key,
        "outward_issue": outward_issue_key,
        "link_type": link_type,
    }
