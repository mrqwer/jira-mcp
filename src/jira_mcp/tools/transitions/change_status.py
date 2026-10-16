from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.transitions.list_transitions import list_transitions


@mcp.tool()
def change_status(issue_key: str, new_status_name: str) -> dict[str, Any]:
    """Transition an issue by transition ID, transition name, or target status name."""
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
            }
            for item in transitions
        ]
        raise ValueError(
            f"Transition {new_status_name!r} is unavailable. Available: {available}"
        )

    client.request(
        "POST",
        client.issue_path(issue_key, "/transitions"),
        expected=(204,),
        json={"transition": {"id": transition["id"]}},
    )
    return {
        "key": issue_key,
        "transition_id": transition["id"],
        "status": transition.get("to", {}).get("name"),
    }
