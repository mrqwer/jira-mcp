from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def delete_attachment(attachment_id: str) -> dict[str, Any]:
    """Permanently delete a Jira attachment by its ID."""
    client.request(
        "DELETE",
        f"attachment/{quote(attachment_id, safe='')}",
        expected=(204,),
    )
    return {"deleted_attachment_id": attachment_id}
