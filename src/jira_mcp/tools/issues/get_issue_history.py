from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_issue_history(
    issue_key: str,
    field: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return an issue's change history: who changed which field, when, from what to what.

    field keeps only changes of one field, e.g. "status" or "assignee".
    limit keeps the most recent changes (1-100). Changes are oldest first."""
    data = client.request(
        "GET",
        client.issue_path(issue_key),
        params={"expand": "changelog", "fields": "summary"},
    )
    changelog = data.get("changelog", {})
    histories = changelog.get("histories", [])
    wanted = field.casefold() if field else None

    changes = []
    for history in histories:
        items = [
            {
                "field": item.get("field"),
                "from": item.get("fromString", item.get("from")),
                "to": item.get("toString", item.get("to")),
            }
            for item in history.get("items", [])
            if not wanted or item.get("field", "").casefold() == wanted
        ]
        if items:
            author = history.get("author") or {}
            changes.append(
                {
                    "id": history.get("id"),
                    "author": author.get("displayName"),
                    "author_username": author.get("name"),
                    "created": history.get("created"),
                    "items": items,
                }
            )

    limit = max(1, min(limit, 100))
    return {
        "key": data.get("key", issue_key),
        "matching_changes": len(changes),
        "history_complete": changelog.get("total", len(histories)) <= len(histories),
        "changes": changes[-limit:],
    }
