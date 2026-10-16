from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def delete_link(link_id: str) -> dict[str, Any]:
    """Remove a link between two Jira issues by its link ID (issuelinks[].id from get_ticket/search_tickets)."""
    client.request(
        "DELETE",
        f"issueLink/{quote(link_id, safe='')}",
        expected=(204,),
    )
    return {"deleted": True, "link_id": link_id}
