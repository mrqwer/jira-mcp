from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_project_statuses(project_key: str) -> list[dict[str, Any]]:
    """List valid statuses per issue type for a project (the real status set, not per-issue transitions)."""
    return client.request("GET", f"project/{quote(project_key, safe='')}/statuses")
