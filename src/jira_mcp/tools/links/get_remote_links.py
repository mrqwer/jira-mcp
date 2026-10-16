from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_remote_links(issue_key: str) -> list[dict[str, Any]]:
    """List remote links attached to an issue, such as Confluence or repository URLs."""
    data = client.request("GET", client.issue_path(issue_key, "/remotelink"))
    return data if isinstance(data, list) else [data]
