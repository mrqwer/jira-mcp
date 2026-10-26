from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_fields(query: str | None = None, custom_only: bool = False) -> list[dict[str, Any]]:
    """List Jira fields with their ids, names, JQL names and value types.

    Use it to map customfield_XXXXX ids to human names (and back) before
    reading or setting custom fields. query filters by a case-insensitive
    substring of the field name or id; custom_only keeps custom fields only."""
    wanted = query.casefold() if query else None
    result = []
    for field in client.request("GET", "field"):
        if custom_only and not field.get("custom"):
            continue
        if wanted and not (
            wanted in field.get("name", "").casefold()
            or wanted in field.get("id", "").casefold()
        ):
            continue
        schema = field.get("schema") or {}
        result.append(
            {
                "id": field.get("id"),
                "name": field.get("name"),
                "custom": field.get("custom", False),
                "jql_names": field.get("clauseNames", []),
                "type": schema.get("type"),
                "items": schema.get("items"),
                "custom_type": schema.get("custom"),
            }
        )
    return result
