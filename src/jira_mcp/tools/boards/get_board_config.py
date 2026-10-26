from __future__ import annotations

from typing import Any

from jira_mcp import client
from jira_mcp.app import mcp


@mcp.tool()
def get_board_config(board_id: int) -> dict[str, Any]:
    """Return a board's columns and which statuses each column shows.

    A board column is not a status: one column can hold several statuses,
    and its name can differ from theirs. Use this to answer "which column is
    the issue in" or "which status puts it in column X"."""
    config = client.request("GET", f"board/{board_id}/configuration", api="agile")
    status_names = {
        str(status.get("id")): status.get("name") for status in client.request("GET", "status")
    }

    columns = []
    for column in config.get("columnConfig", {}).get("columns", []):
        statuses = [
            {"id": str(s.get("id")), "name": status_names.get(str(s.get("id")))}
            for s in column.get("statuses", [])
        ]
        entry: dict[str, Any] = {"name": column.get("name"), "statuses": statuses}
        if "min" in column or "max" in column:
            entry["limits"] = {"min": column.get("min"), "max": column.get("max")}
        columns.append(entry)

    return {
        "id": config.get("id"),
        "name": config.get("name"),
        "type": config.get("type"),
        "filter_id": (config.get("filter") or {}).get("id"),
        "sub_query": (config.get("subQuery") or {}).get("query"),
        "columns": columns,
    }
