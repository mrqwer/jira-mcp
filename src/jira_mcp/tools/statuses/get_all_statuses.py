from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_all_statuses() -> list[dict[str, Any]]:
    """List every status defined in this Jira instance, across all projects."""
    return client.request("GET", "status")
