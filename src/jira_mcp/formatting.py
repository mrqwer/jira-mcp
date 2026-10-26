from __future__ import annotations

from typing import Any

from jira_mcp import client

ISSUE_LIST_FIELDS = ["summary", "status", "assignee", "issuetype", "priority", "updated"]


def issue_summary(issue: dict[str, Any]) -> dict[str, Any]:
    """Compact one issue from an agile list into the fields an agent needs."""
    fields = issue.get("fields", {})
    key = issue.get("key")
    return {
        "key": key,
        "summary": fields.get("summary"),
        "status": (fields.get("status") or {}).get("name"),
        "assignee": (fields.get("assignee") or {}).get("name"),
        "issue_type": (fields.get("issuetype") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "updated": fields.get("updated"),
        "browse_url": client.browse_url(key),
    }


def issue_page(
    path: str,
    *,
    jql: str | None = None,
    start_at: int = 0,
    max_results: int = 20,
    api: str = "agile",
) -> dict[str, Any]:
    """One page of issues from an agile list endpoint, compacted with issue_summary."""
    params: dict[str, Any] = {"fields": ",".join(ISSUE_LIST_FIELDS)}
    if jql:
        params["jql"] = jql
    page = client.page(
        path, "issues", start_at=start_at, max_results=max_results, params=params, api=api
    )
    page["items"] = [issue_summary(issue) for issue in page["items"]]
    return page


def require_issue_keys(issue_keys: list[str], limit: int = 50) -> list[str]:
    if not issue_keys:
        raise ValueError("Pass at least one issue key")
    if len(issue_keys) > limit:
        raise ValueError(f"Pass at most {limit} issue keys per call")
    return issue_keys
