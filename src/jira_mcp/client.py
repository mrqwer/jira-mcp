from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import quote

import requests

from jira_mcp import config


@lru_cache(maxsize=1)
def session() -> requests.Session:
    settings = {
        "JIRA_URL": config.JIRA_URL,
        "JIRA_USER": config.JIRA_USER,
        "JIRA_PASSWORD": config.JIRA_PASSWORD,
    }
    missing = [name for name in config.REQUIRED_SETTINGS if not settings[name]]
    if missing:
        raise RuntimeError(
            f"Missing Jira settings: {', '.join(missing)}. Pass them in the MCP "
            f"server env or set them in {config.ENV_FILE} (see .env.example)"
        )

    http = requests.Session()
    http.headers["Accept"] = "application/json"

    http.auth = (config.JIRA_USER, config.JIRA_PASSWORD)
    http.verify = config.JIRA_VERIFY_SSL
    return http


def request(
    method: str,
    path: str,
    *,
    expected: tuple[int, ...] = (200,),
    **kwargs: Any,
) -> Any:
    url = f"{config.JIRA_URL}/rest/api/2/{path.lstrip('/')}"

    try:
        response = session().request(
            method, url, timeout=config.JIRA_TIMEOUT, **kwargs
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Jira request failed: {exc}") from exc

    if response.status_code not in expected:
        detail = response.text.strip()[:2000] or response.reason
        raise RuntimeError(
            f"Jira returned HTTP {response.status_code} for "
            f"{method.upper()} {path}: {detail}"
        )

    if not response.content:
        return {}

    try:
        return response.json()
    except requests.JSONDecodeError as exc:
        raise RuntimeError("Jira returned a non-JSON response") from exc


def issue_path(issue_key: str, suffix: str = "") -> str:
    return f"issue/{quote(issue_key, safe='')}{suffix}"


def browse_url(issue_key: str) -> str:
    return f"{config.JIRA_URL}/browse/{issue_key}"


def bounded_results(value: int) -> int:
    return max(1, min(value, config.JIRA_MAX_RESULTS))
