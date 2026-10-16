"""Entry point kept at the repo root so MCP configs can point at main.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from jira_mcp.server import main  # noqa: E402

if __name__ == "__main__":
    main()
