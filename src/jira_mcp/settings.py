from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REQUIRED_SETTINGS = ("JIRA_URL", "JIRA_USER", "JIRA_PASSWORD")
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value and value.strip() else default


# Variables passed by the MCP client ("env" in its config) win over the local .env.
load_dotenv(ENV_FILE, override=False)

JIRA_URL = os.environ.get("JIRA_URL", "").rstrip("/")
JIRA_USER = os.environ.get("JIRA_USER", "")
JIRA_PASSWORD = os.environ.get("JIRA_PASSWORD", "")
JIRA_VERIFY_SSL = env_bool("JIRA_VERIFY_SSL", True)
JIRA_TIMEOUT = env_int("JIRA_TIMEOUT", 20)
JIRA_MAX_RESULTS = env_int("JIRA_MAX_RESULTS", 50)
