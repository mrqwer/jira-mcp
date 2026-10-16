from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def delete_comment(issue_key: str, comment_id: str) -> dict[str, Any]:
    """Permanently delete a Jira comment by its ID."""
    client.request(
        "DELETE",
        client.issue_path(issue_key, f"/comment/{quote(comment_id, safe='')}"),
        expected=(204,),
    )
    return {"deleted": True, "comment_id": comment_id}
