from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.transitions.list_transitions import list_transitions


@mcp.tool()
def change_status(
    issue_key: str,
    new_status_name: str,
    fields: dict[str, Any] | None = None,
    comment: str | None = None,
) -> dict[str, Any]:
    """Transition an issue by transition ID, transition name, or target status name.

    Some transitions have screen fields that must be filled, most often
    resolution when closing: pass them in fields, e.g.
    {"resolution": {"name": "Done"}}. list_transitions shows each
    transition's fields and which are required. comment is added to the
    issue as part of the same transition."""
    wanted = new_status_name.casefold()
    transitions = list_transitions(issue_key)
    transition = next(
        (
            item
            for item in transitions
            if str(item.get("id")) == new_status_name
            or item.get("name", "").casefold() == wanted
            or item.get("to", {}).get("name", "").casefold() == wanted
        ),
        None,
    )
    if not transition:
        available = [
            {
                "id": item.get("id"),
                "transition": item.get("name"),
                "to_status": item.get("to", {}).get("name"),
                "required_fields": sorted(
                    name
                    for name, meta in item.get("fields", {}).items()
                    if meta.get("required")
                ),
            }
            for item in transitions
        ]
        raise ValueError(
            f"Transition {new_status_name!r} is unavailable. Available: {available}"
        )

    payload: dict[str, Any] = {"transition": {"id": transition["id"]}}
    if fields:
        payload["fields"] = fields
    if comment:
        payload["update"] = {"comment": [{"add": {"body": comment}}]}

    client.request(
        "POST",
        client.issue_path(issue_key, "/transitions"),
        expected=(204,),
        json=payload,
    )
    return {
        "key": issue_key,
        "transition_id": transition["id"],
        "status": transition.get("to", {}).get("name"),
        "updated_fields": sorted(fields or {}),
        "commented": bool(comment),
    }
