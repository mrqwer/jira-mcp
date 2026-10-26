from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def delete_remote_link(issue_key: str, link_id: str) -> dict[str, Any]:
    """Remove an external link from an issue by its id (from get_remote_links)."""
    client.request(
        "DELETE",
        client.issue_path(issue_key, f"/remotelink/{quote(str(link_id), safe='')}"),
        expected=(204,),
    )
    return {"deleted": True, "remote_link_id": link_id}
