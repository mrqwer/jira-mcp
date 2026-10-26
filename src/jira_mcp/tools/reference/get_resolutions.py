from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_resolutions() -> list[dict[str, Any]]:
    """List valid resolutions, e.g. for change_status fields={"resolution": {"name": ...}}."""
    return [
        {"id": r.get("id"), "name": r.get("name"), "description": r.get("description")}
        for r in client.request("GET", "resolution")
    ]
