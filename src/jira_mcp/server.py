from __future__ import annotations

from jira_mcp import tools  # noqa: F401  (importing registers every tool)
from jira_mcp.app import mcp


def main() -> None:
    mcp.run(transport="stdio")
