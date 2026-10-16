from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from jira_mcp import client, config
from jira_mcp.app import mcp


@mcp.tool()
def download_attachment(attachment_id: str, save_path: str | None = None) -> dict[str, Any]:
    """Download a Jira attachment by its ID to a local file.

    Defaults to saving under the attachment's original filename in the
    current directory when save_path is omitted."""
    meta = client.request("GET", f"attachment/{quote(attachment_id, safe='')}")
    content_url = meta.get("content")
    if not content_url:
        raise RuntimeError(f"Attachment {attachment_id} has no content URL")

    try:
        response = client.session().get(content_url, timeout=config.JIRA_TIMEOUT)
    except requests.RequestException as exc:
        raise RuntimeError(f"Jira attachment download failed: {exc}") from exc

    if response.status_code != 200:
        detail = response.text.strip()[:2000] or response.reason
        raise RuntimeError(
            f"Jira returned HTTP {response.status_code} downloading "
            f"attachment {attachment_id}: {detail}"
        )

    path = Path(save_path) if save_path else Path(meta.get("filename", attachment_id))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)

    return {
        "attachment_id": attachment_id,
        "filename": meta.get("filename"),
        "mime_type": meta.get("mimeType"),
        "size": meta.get("size"),
        "saved_to": str(path.resolve()),
    }
