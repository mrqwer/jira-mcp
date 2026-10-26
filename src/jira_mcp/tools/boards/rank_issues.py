from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp
from jira_mcp.formatting import require_issue_keys


@mcp.tool()
def rank_issues(
    issue_keys: list[str],
    before_issue_key: str | None = None,
    after_issue_key: str | None = None,
) -> dict[str, Any]:
    """Reorder issues on boards and backlogs: place them before or after another issue.

    Pass exactly one of before_issue_key or after_issue_key (up to 50 issues)."""
    require_issue_keys(issue_keys)
    if bool(before_issue_key) == bool(after_issue_key):
        raise ValueError("Pass exactly one of before_issue_key or after_issue_key")

    payload: dict[str, Any] = {"issues": issue_keys}
    if before_issue_key:
        payload["rankBeforeIssue"] = before_issue_key
    else:
        payload["rankAfterIssue"] = after_issue_key

    # 207 means some issues could not be ranked; the body lists them.
    result = client.request(
        "PUT", "issue/rank", expected=(204, 207), json=payload, api="agile"
    )
    return {"ranked": issue_keys, "errors": result.get("entries", []) if result else []}
