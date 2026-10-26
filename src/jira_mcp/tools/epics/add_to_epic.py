from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.formatting import require_issue_keys


@mcp.tool()
def add_to_epic(epic_key: str, issue_keys: list[str]) -> dict[str, Any]:
    """Add issues (up to 50) to an epic, replacing their current epic if any."""
    require_issue_keys(issue_keys)
    client.request(
        "POST",
        f"epic/{quote(epic_key, safe='')}/issue",
        expected=(204,),
        json={"issues": issue_keys},
        api="agile",
    )
    return {"epic": epic_key, "added": issue_keys}
