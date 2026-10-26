from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def add_remote_link(
    issue_key: str,
    url: str,
    title: str,
    summary: str | None = None,
) -> dict[str, Any]:
    """Attach an external link to an issue, e.g. a pull request, document or build."""
    link: dict[str, Any] = {"url": url, "title": title}
    if summary:
        link["summary"] = summary
    data = client.request(
        "POST",
        client.issue_path(issue_key, "/remotelink"),
        expected=(200, 201),
        json={"object": link},
    )
    return {"key": issue_key, "remote_link_id": data.get("id"), "url": url}
