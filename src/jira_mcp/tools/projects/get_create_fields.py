from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_create_fields(project_key: str, issue_type: str) -> dict[str, Any]:
    """Return required and optional create fields for one project and issue type.

    issue_type is the type name as shown in Jira (localized, e.g. "Задача") or its id."""
    # createmeta's issuetypeNames only matches untranslated names, so resolve
    # the visible (possibly localized) name to an id first.
    meta = client.request(
        "GET",
        "issue/createmeta",
        params={"projectKeys": project_key, "expand": "projects.issuetypes"},
    )
    projects = meta.get("projects", [])
    types = projects[0].get("issuetypes", []) if projects else []
    wanted = issue_type.casefold()
    match = next(
        (
            t
            for t in types
            if str(t.get("id")) == issue_type or t.get("name", "").casefold() == wanted
        ),
        None,
    )
    if not match:
        available = [t.get("name") for t in types]
        raise ValueError(
            f"Issue type {issue_type!r} is unavailable in project {project_key!r}. "
            f"Available: {available}"
        )

    data = client.request(
        "GET",
        "issue/createmeta",
        params={
            "projectKeys": project_key,
            "issuetypeIds": match["id"],
            "expand": "projects.issuetypes.fields",
        },
    )
    projects = data.get("projects", [])
    issue_types = projects[0].get("issuetypes", []) if projects else []
    if not issue_types:
        raise ValueError(
            f"Issue type {issue_type!r} is unavailable in project {project_key!r}"
        )
    return issue_types[0]
