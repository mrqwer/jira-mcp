from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.versions.list_versions import version_summary


@mcp.tool()
def create_version(
    project_key: str,
    name: str,
    description: str | None = None,
    start_date: str | None = None,
    release_date: str | None = None,
) -> dict[str, Any]:
    """Create an unreleased version in a project. Dates use YYYY-MM-DD."""
    payload: dict[str, Any] = {"project": project_key.upper(), "name": name}
    if description:
        payload["description"] = description
    if start_date:
        payload["startDate"] = start_date
    if release_date:
        payload["releaseDate"] = release_date

    return version_summary(
        client.request("POST", "version", expected=(201,), json=payload)
    )
