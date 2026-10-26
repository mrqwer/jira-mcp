from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


def version_summary(version: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": version.get("id"),
        "name": version.get("name"),
        "description": version.get("description"),
        "released": version.get("released", False),
        "archived": version.get("archived", False),
        "start_date": version.get("startDate"),
        "release_date": version.get("releaseDate"),
    }


@mcp.tool()
def list_versions(
    project_key: str,
    released: bool | None = None,
    include_archived: bool = False,
) -> list[dict[str, Any]]:
    """List a project's versions (the values of fixVersion / affectedVersion).

    released=false keeps unreleased versions, released=true released ones.
    Archived versions are skipped unless include_archived is true."""
    versions = client.request("GET", f"project/{quote(project_key, safe='')}/versions")
    return [
        version_summary(v)
        for v in versions
        if (include_archived or not v.get("archived"))
        and (released is None or bool(v.get("released")) == released)
    ]
