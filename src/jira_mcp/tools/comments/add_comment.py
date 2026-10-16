from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def add_comment(
    issue_key: str,
    comment_text: str,
    comment_id: str | None = None,
) -> dict[str, Any]:
    """Add a Jira comment, or update one when comment_id is provided."""
    if comment_id:
        return client.request(
            "PUT",
            client.issue_path(issue_key, f"/comment/{quote(comment_id, safe='')}"),
            expected=(200,),
            json={"body": comment_text},
        )
    return client.request(
        "POST",
        client.issue_path(issue_key, "/comment"),
        expected=(201,),
        json={"body": comment_text},
    )
