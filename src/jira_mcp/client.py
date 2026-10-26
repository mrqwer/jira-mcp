from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import quote

import requests

from jira_mcp import settings


@lru_cache(maxsize=1)
def session() -> requests.Session:
    values = {
        "JIRA_URL": settings.JIRA_URL,
        "JIRA_USER": settings.JIRA_USER,
        "JIRA_PASSWORD": settings.JIRA_PASSWORD,
    }
    missing = [name for name in settings.REQUIRED_SETTINGS if not values[name]]
    if missing:
        raise RuntimeError(
            f"Missing Jira settings: {', '.join(missing)}. Pass them in the MCP "
            f"server env or set them in {settings.ENV_FILE} (see .env.example)"
        )

    http = requests.Session()
    http.headers["Accept"] = "application/json"

    http.auth = (settings.JIRA_USER, settings.JIRA_PASSWORD)
    http.verify = settings.JIRA_VERIFY_SSL
    return http


def request(
    method: str,
    path: str,
    *,
    expected: tuple[int, ...] = (200,),
    **kwargs: Any,
) -> Any:
    url = f"{settings.JIRA_URL}/rest/api/2/{path.lstrip('/')}"

    try:
        response = session().request(
            method, url, timeout=settings.JIRA_TIMEOUT, **kwargs
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
    return f"{settings.JIRA_URL}/browse/{issue_key}"


def bounded_results(value: int) -> int:
    return max(1, min(value, settings.JIRA_MAX_RESULTS))
