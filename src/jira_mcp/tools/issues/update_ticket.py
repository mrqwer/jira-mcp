from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def update_ticket(
    issue_key: str,
    fields: dict[str, Any] | None = None,
    update: dict[str, list[dict[str, Any]]] | None = None,
    notify_users: bool = True,
) -> dict[str, Any]:
    """Update Jira issue fields.

    fields replaces whole values, e.g. {"summary": "New title"}.
    update applies operations without overwriting the rest of the value, e.g.
    {"labels": [{"add": "backend"}, {"remove": "old"}],
     "components": [{"add": {"name": "API"}}]}.
    A field may appear in only one of them. Use get_edit_fields to see which
    fields are editable and which operations they support."""
    if not fields and not update:
        raise ValueError("Pass fields, update, or both")
    overlap = sorted(set(fields or {}) & set(update or {}))
    if overlap:
        raise ValueError(f"Fields cannot be in both fields and update: {overlap}")

    payload: dict[str, Any] = {}
    if fields:
        payload["fields"] = fields
    if update:
        payload["update"] = update

    client.request(
        "PUT",
        client.issue_path(issue_key),
        expected=(204,),
        params={"notifyUsers": str(notify_users).lower()},
        json=payload,
    )
    return {
        "key": issue_key,
        "updated_fields": sorted(fields or {}),
        "update_operations": sorted(update or {}),
    }
