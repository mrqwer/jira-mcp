from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.issues.search_tickets import search_tickets


@mcp.tool()
def run_filter(
    filter_id: str,
    max_results: int = 10,
    start_at: int = 0,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Run a saved filter by id and return its issues, like search_tickets with the filter's JQL."""
    saved = client.request("GET", f"filter/{quote(str(filter_id), safe='')}")
    result = search_tickets(
        saved["jql"], max_results=max_results, start_at=start_at, fields=fields
    )
    result["filter"] = {"id": saved.get("id"), "name": saved.get("name"), "jql": saved.get("jql")}
    return result
