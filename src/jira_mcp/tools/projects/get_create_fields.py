from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_create_fields(project_key: str, issue_type: str) -> dict[str, Any]:
    """Return required and optional create fields for one project and issue type."""
    data = client.request(
        "GET",
        "issue/createmeta",
        params={
            "projectKeys": project_key,
            "issuetypeNames": issue_type,
            "expand": "projects.issuetypes.fields",
        },
    )
    projects = data.get("projects", [])
    issue_types = projects[0].get("issuetypes", []) if projects else []
    if not issue_types:
        raise ValueError(
            f"Issue type {issue_type!r} is unavailable in project {project_key!r}"
        )
    return issue_types[0]
