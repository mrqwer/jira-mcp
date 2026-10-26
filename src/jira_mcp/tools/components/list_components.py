from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


def component_summary(component: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": component.get("id"),
        "name": component.get("name"),
        "description": component.get("description"),
        "lead": (component.get("lead") or {}).get("name"),
        "assignee_type": component.get("assigneeType"),
    }


@mcp.tool()
def list_components(project_key: str) -> list[dict[str, Any]]:
    """List a project's components (use their names in the components field)."""
    components = client.request(
        "GET", f"project/{quote(project_key, safe='')}/components"
    )
    return [component_summary(c) for c in components]
