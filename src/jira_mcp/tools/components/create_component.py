from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.tools.components.list_components import component_summary


@mcp.tool()
def create_component(
    project_key: str,
    name: str,
    description: str | None = None,
    lead_username: str | None = None,
) -> dict[str, Any]:
    """Create a component in a project, optionally with a lead (Jira username)."""
    payload: dict[str, Any] = {"project": project_key.upper(), "name": name}
    if description:
        payload["description"] = description
    if lead_username:
        payload["leadUserName"] = lead_username

    return component_summary(
        client.request("POST", "component", expected=(201,), json=payload)
    )
