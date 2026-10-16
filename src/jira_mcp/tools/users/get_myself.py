from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_myself() -> dict[str, Any]:
    """Return the authenticated Jira user's account and permission-visible profile."""
    return client.request("GET", "myself")
