from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_priorities() -> list[dict[str, Any]]:
    """List valid issue priorities (use the name in create_ticket or update_ticket)."""
    return [
        {"id": p.get("id"), "name": p.get("name"), "description": p.get("description")}
        for p in client.request("GET", "priority")
    ]
