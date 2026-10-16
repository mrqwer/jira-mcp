from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def list_projects(max_results: int = 50) -> list[dict[str, Any]]:
    """List Jira projects visible to the authenticated user."""
    projects = client.request("GET", "project")
    return projects[: client.bounded_results(max_results)]
