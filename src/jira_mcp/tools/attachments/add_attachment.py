from __future__ import annotations

from pathlib import Path
from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def add_attachment(issue_key: str, file_path: str) -> dict[str, Any]:
    """Upload a local file as an attachment to a Jira issue."""
    path = Path(file_path)
    if not path.is_file():
        raise ValueError(f"File not found: {file_path}")

    with path.open("rb") as fh:
        data = client.request(
            "POST",
            client.issue_path(issue_key, "/attachments"),
            headers={"X-Atlassian-Token": "no-check"},
            files={"file": (path.name, fh)},
        )

    return data[0] if isinstance(data, list) and len(data) == 1 else data
