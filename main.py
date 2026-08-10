from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import quote

import requests
from mcp.server.fastmcp import FastMCP

try:
    from config import (
        JIRA_MAX_RESULTS,
        JIRA_PASSWORD,
        JIRA_TIMEOUT,
        JIRA_URL,
        JIRA_USER,
        JIRA_VERIFY_SSL,
    )
except ModuleNotFoundError as exc:
    if exc.name == "config":
        raise RuntimeError(
            "Create config.py from config.example.py and add your Jira credentials"
        ) from exc
    raise

mcp = FastMCP("Corporate Jira")

DEFAULT_ISSUE_FIELDS = [
    "summary",
    "description",
    "status",
    "assignee",
    "reporter",
    "issuetype",
    "priority",
    "labels",
    "components",
    "fixVersions",
    "parent",
    "subtasks",
    "created",
    "updated",
    "duedate",
    "comment",
    "issuelinks",
    "attachment",
    "timetracking",
]


def _jira_url() -> str:
    return JIRA_URL


@lru_cache(maxsize=1)
def _client() -> requests.Session:
    session = requests.Session()
    session.headers["Accept"] = "application/json"

    session.auth = (JIRA_USER, JIRA_PASSWORD)
    session.verify = JIRA_VERIFY_SSL
    return session


def _request(
    method: str,
    path: str,
    *,
    expected: tuple[int, ...] = (200,),
    **kwargs: Any,
) -> Any:
    url = f"{_jira_url()}/rest/api/2/{path.lstrip('/')}"
    timeout = JIRA_TIMEOUT

    try:
        response = _client().request(method, url, timeout=timeout, **kwargs)
    except requests.RequestException as exc:
        raise RuntimeError(f"Jira request failed: {exc}") from exc

    if response.status_code not in expected:
        detail = response.text.strip()[:2000] or response.reason
        raise RuntimeError(
            f"Jira returned HTTP {response.status_code} for "
            f"{method.upper()} {path}: {detail}"
        )

    if not response.content:
        return {}

    try:
        return response.json()
    except requests.JSONDecodeError as exc:
        raise RuntimeError("Jira returned a non-JSON response") from exc


def _issue_path(issue_key: str, suffix: str = "") -> str:
    return f"issue/{quote(issue_key, safe='')}{suffix}"


def _browse_url(issue_key: str) -> str:
    return f"{_jira_url()}/browse/{issue_key}"


def _bounded_results(value: int) -> int:
    limit = JIRA_MAX_RESULTS
    return max(1, min(value, limit))


@mcp.tool()
def get_myself() -> dict[str, Any]:
    """Return the authenticated Jira user's account and permission-visible profile."""
    return _request("GET", "myself")


@mcp.tool()
def list_projects(max_results: int = 50) -> list[dict[str, Any]]:
    """List Jira projects visible to the authenticated user."""
    projects = _request("GET", "project")
    return projects[: _bounded_results(max_results)]


@mcp.tool()
def get_project_issue_types(project_key: str) -> dict[str, Any]:
    """List issue types that can be created in a Jira project."""
    data = _request(
        "GET",
        "issue/createmeta",
        params={"projectKeys": project_key, "expand": "projects.issuetypes"},
    )
    projects = data.get("projects", [])
    if not projects:
        raise ValueError(f"Project {project_key!r} is unavailable or not creatable")
    return projects[0]


@mcp.tool()
def get_create_fields(project_key: str, issue_type: str) -> dict[str, Any]:
    """Return required and optional create fields for one project and issue type."""
    data = _request(
        "GET",
        "issue/createmeta",
        params={
            "projectKeys": project_key,
            "issuetypeNames": issue_type,
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


@mcp.tool()
def find_users(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Find Jira users by username, display name, or email fragment."""
    data = _request(
        "GET",
        "user/picker",
        params={"query": query, "maxResults": _bounded_results(max_results)},
    )
    return data.get("users", [])


@mcp.tool()
def get_ticket(
    issue_key: str,
    fields: list[str] | None = None,
    comment_limit: int = 10,
) -> dict[str, Any]:
    """Get an issue with useful fields, links, attachments, and recent comments."""
    data = _request(
        "GET",
        _issue_path(issue_key),
        params={
            "fields": ",".join(fields or DEFAULT_ISSUE_FIELDS),
            "expand": "names,schema",
        },
    )

    comments = data.get("fields", {}).get("comment")
    if comments and "comments" in comments:
        limit = max(0, min(comment_limit, 50))
        comments["comments"] = comments["comments"][-limit:] if limit else []

    data["browse_url"] = _browse_url(data.get("key", issue_key))
    return data


@mcp.tool()
def search_tickets(
    jql_query: str,
    max_results: int = 10,
    start_at: int = 0,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Search Jira with JQL. Results are capped by JIRA_MAX_RESULTS (default 50)."""
    data = _request(
        "GET",
        "search",
        params={
            "jql": jql_query,
            "startAt": max(0, start_at),
            "maxResults": _bounded_results(max_results),
            "fields": ",".join(
                fields
                or [
                    "summary",
                    "status",
                    "assignee",
                    "issuetype",
                    "priority",
                    "updated",
                ]
            ),
        },
    )
    for issue in data.get("issues", []):
        issue["browse_url"] = _browse_url(issue["key"])
    return data


@mcp.tool()
def create_ticket(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    assignee_username: str | None = None,
    parent_key: str | None = None,
    labels: list[str] | None = None,
    priority: str | None = None,
    additional_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an issue. Use get_create_fields before sending project custom fields."""
    fields = dict(additional_fields or {})
    fields.update(
        {
            "project": {"key": project_key.upper()},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
    )
    if assignee_username:
        fields["assignee"] = {"name": assignee_username}
    if parent_key:
        fields["parent"] = {"key": parent_key}
    if labels is not None:
        fields["labels"] = labels
    if priority:
        fields["priority"] = {"name": priority}

    data = _request("POST", "issue", expected=(201,), json={"fields": fields})
    data["browse_url"] = _browse_url(data["key"])
    return data


@mcp.tool()
def update_ticket(
    issue_key: str,
    fields: dict[str, Any],
    notify_users: bool = True,
) -> dict[str, Any]:
    """Update Jira issue fields using the same field shapes returned by metadata."""
    _request(
        "PUT",
        _issue_path(issue_key),
        expected=(204,),
        params={"notifyUsers": str(notify_users).lower()},
        json={"fields": fields},
    )
    return {"key": issue_key, "updated_fields": sorted(fields)}


@mcp.tool()
def assign_ticket(
    issue_key: str,
    assignee_username: str | None,
) -> dict[str, Any]:
    """Assign an issue by Jira username. Pass null to unassign it."""
    _request(
        "PUT",
        _issue_path(issue_key, "/assignee"),
        expected=(204,),
        json={"name": assignee_username},
    )
    return {"key": issue_key, "assignee": assignee_username}


@mcp.tool()
def add_comment(
    issue_key: str,
    comment_text: str,
    comment_id: str | None = None,
) -> dict[str, Any]:
    """Add a Jira comment, or update one when comment_id is provided."""
    if comment_id:
        return _request(
            "PUT",
            _issue_path(issue_key, f"/comment/{quote(comment_id, safe='')}"),
            expected=(200,),
            json={"body": comment_text},
        )
    return _request(
        "POST",
        _issue_path(issue_key, "/comment"),
        expected=(201,),
        json={"body": comment_text},
    )


@mcp.tool()
def list_transitions(issue_key: str) -> list[dict[str, Any]]:
    """List workflow transitions currently available for an issue."""
    data = _request(
        "GET",
        _issue_path(issue_key, "/transitions"),
        params={"expand": "transitions.fields"},
    )
    return data.get("transitions", [])


@mcp.tool()
def change_status(issue_key: str, new_status_name: str) -> dict[str, Any]:
    """Transition an issue by transition ID, transition name, or target status name."""
    wanted = new_status_name.casefold()
    transitions = list_transitions(issue_key)
    transition = next(
        (
            item
            for item in transitions
            if str(item.get("id")) == new_status_name
            or item.get("name", "").casefold() == wanted
            or item.get("to", {}).get("name", "").casefold() == wanted
        ),
        None,
    )
    if not transition:
        available = [
            {
                "id": item.get("id"),
                "transition": item.get("name"),
                "to_status": item.get("to", {}).get("name"),
            }
            for item in transitions
        ]
        raise ValueError(
            f"Transition {new_status_name!r} is unavailable. Available: {available}"
        )

    _request(
        "POST",
        _issue_path(issue_key, "/transitions"),
        expected=(204,),
        json={"transition": {"id": transition["id"]}},
    )
    return {
        "key": issue_key,
        "transition_id": transition["id"],
        "status": transition.get("to", {}).get("name"),
    }


@mcp.tool()
def add_worklog(
    issue_key: str,
    time_spent: str,
    comment: str = "",
    started: str | None = None,
) -> dict[str, Any]:
    """Log work such as '1h 30m'. started uses Jira's ISO-like timestamp format."""
    payload: dict[str, Any] = {"timeSpent": time_spent}
    if comment:
        payload["comment"] = comment
    if started:
        payload["started"] = started
    return _request(
        "POST",
        _issue_path(issue_key, "/worklog"),
        expected=(201,),
        json=payload,
    )


@mcp.tool()
def get_link_types() -> list[dict[str, Any]]:
    """List valid Jira issue-link types and their inward/outward wording."""
    return _request("GET", "issueLinkType").get("issueLinkTypes", [])


@mcp.tool()
def link_tickets(
    inward_issue_key: str,
    outward_issue_key: str,
    link_type: str,
    comment: str | None = None,
) -> dict[str, Any]:
    """Create a typed relationship between two Jira issues."""
    payload: dict[str, Any] = {
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue_key},
        "outwardIssue": {"key": outward_issue_key},
    }
    if comment:
        payload["comment"] = {"body": comment}
    _request("POST", "issueLink", expected=(201,), json=payload)
    return {
        "inward_issue": inward_issue_key,
        "outward_issue": outward_issue_key,
        "link_type": link_type,
    }


@mcp.tool()
def get_remote_links(issue_key: str) -> list[dict[str, Any]]:
    """List remote links attached to an issue, such as Confluence or repository URLs."""
    data = _request("GET", _issue_path(issue_key, "/remotelink"))
    return data if isinstance(data, list) else [data]


if __name__ == "__main__":
    mcp.run(transport="stdio")
