from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_project_issue_types(project_key: str) -> dict[str, Any]:
    """List issue types that can be created in a Jira project."""
    data = client.request(
        "GET",
        "issue/createmeta",
        params={"projectKeys": project_key, "expand": "projects.issuetypes"},
    )
    projects = data.get("projects", [])
    if not projects:
        raise ValueError(f"Project {project_key!r} is unavailable or not creatable")
    return projects[0]
