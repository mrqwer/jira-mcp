from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.versions.list_versions import version_summary


@mcp.tool()
def release_version(version_id: str, release_date: str | None = None) -> dict[str, Any]:
    """Mark a version as released. release_date uses YYYY-MM-DD and defaults to today.

    Get version ids from list_versions."""
    return version_summary(
        client.request(
            "PUT",
            f"version/{quote(str(version_id), safe='')}",
            json={"released": True, "releaseDate": release_date or date.today().isoformat()},
        )
    )
