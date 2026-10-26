from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_edit_fields(issue_key: str) -> dict[str, Any]:
    """Return the fields that can be edited on this issue.

    Each field lists whether it is required, its allowed values and the
    update operations it supports (set/add/remove). Use it before
    update_ticket to pick the right value shape and operation."""
    data = client.request("GET", client.issue_path(issue_key, "/editmeta"))
    return data.get("fields", {})
