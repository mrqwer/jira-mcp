from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import quote

import requests

from jira_mcp import settings

API_BASES = {
    "api": "rest/api/2",
    "agile": "rest/agile/1.0",
}


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
    api: str = "api",
    **kwargs: Any,
) -> Any:
    """Call Jira REST. api="agile" targets /rest/agile/1.0 (boards, sprints, epics)."""
    if api not in API_BASES:
        raise ValueError(f"Unknown Jira API {api!r}; expected one of {sorted(API_BASES)}")
    url = f"{settings.JIRA_URL}/{API_BASES[api]}/{path.lstrip('/')}"

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


def page(
    path: str,
    items_key: str,
    *,
    start_at: int = 0,
    max_results: int = 20,
    params: dict[str, Any] | None = None,
    api: str = "api",
) -> dict[str, Any]:
    """Fetch one page of a paginated Jira list and normalize its shape.

    Handles both the core API ({startAt, maxResults, total, <items_key>}) and
    the agile API ({startAt, maxResults, isLast, values}). The caller passes
    next_start_at back as start_at to continue; it is None on the last page.
    """
    start = max(0, start_at)
    size = bounded_results(max_results)
    data = request(
        "GET",
        path,
        params={**(params or {}), "startAt": start, "maxResults": size},
        api=api,
    )

    items = data.get(items_key, [])
    start = data.get("startAt", start)
    total = data.get("total")
    if not items:
        is_last = True
    elif "isLast" in data:
        is_last = bool(data["isLast"])
    elif total is not None:
        is_last = start + len(items) >= total
    else:
        is_last = len(items) < size

    return {
        "items": items,
        "start_at": start,
        "max_results": size,
        "total": total,
        "next_start_at": None if is_last else start + len(items),
    }
