from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_my_permissions(
    project_key: str | None = None,
    issue_key: str | None = None,
    permission: str | None = None,
) -> dict[str, Any]:
    """Show which Jira permissions the authenticated user has.

    Scope it with project_key or issue_key; without them, global context is
    used. permission checks a single key, e.g. "TRANSITION_ISSUES" or
    "EDIT_ISSUES". Use it to explain why Jira rejected an action."""
    params: dict[str, Any] = {}
    if project_key:
        params["projectKey"] = project_key
    if issue_key:
        params["issueKey"] = issue_key

    permissions = client.request("GET", "mypermissions", params=params).get(
        "permissions", {}
    )

    if permission:
        key = permission.upper()
        if key not in permissions:
            raise ValueError(f"Unknown Jira permission {key!r}")
        return {
            "permission": key,
            "name": permissions[key].get("name"),
            "granted": bool(permissions[key].get("havePermission")),
        }

    return {
        "granted": sorted(k for k, v in permissions.items() if v.get("havePermission")),
        "denied": sorted(k for k, v in permissions.items() if not v.get("havePermission")),
    }
