from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_link_types() -> list[dict[str, Any]]:
    """List valid Jira issue-link types and their inward/outward wording."""
    return client.request("GET", "issueLinkType").get("issueLinkTypes", [])
