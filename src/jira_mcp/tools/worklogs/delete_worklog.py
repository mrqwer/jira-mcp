from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def delete_worklog(issue_key: str, worklog_id: str) -> dict[str, Any]:
    """Permanently delete a worklog entry. Get ids from get_worklogs."""
    client.request(
        "DELETE",
        client.issue_path(issue_key, f"/worklog/{quote(str(worklog_id), safe='')}"),
        expected=(204,),
    )
    return {"deleted": True, "worklog_id": worklog_id}
