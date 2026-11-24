"""Read-only client for listing issues from GitHub repositories."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_REPOSITORY_PART = re.compile(r"^[A-Za-z0-9_.-]+$")


class GitHubAPIError(RuntimeError):
    """Raised when GitHub cannot return repository issue data."""


def normalize_repository(repository: str) -> str:
    """Validate a GitHub repository name or URL and return owner/name."""
    value = repository.strip() if isinstance(repository, str) else ""
    if not value:
        raise ValueError("Provide a GitHub repository as owner/name or a GitHub URL.")

    if "://" in value:
        parsed = urlparse(value)
        if (
            parsed.scheme != "https"
            or parsed.hostname not in {"github.com", "www.github.com"}
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Use an https://github.com/owner/repo URL.")
        parts = parsed.path.strip("/").split("/")
    else:
        parts = value.split("/")

    if len(parts) != 2:
        raise ValueError("Repository must be owner/name or a URL to the repository root.")

    owner, name = parts
    if name.lower().endswith(".git"):
        name = name[:-4]

    for part in (owner, name):
        if not part or part in {".", ".."} or not _REPOSITORY_PART.fullmatch(part):
            raise ValueError("Repository owner and name contain invalid characters.")

    return f"{owner}/{name}"


def _error_message(error: HTTPError) -> str:
    detail = ""
    try:
        payload = json.loads(error.read().decode("utf-8"))
        if isinstance(payload, dict):
            detail = str(payload.get("message", "")).strip()
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
        pass

    if error.code in {403, 429}:
        message = (
            "GitHub refused the request, possibly because the API rate limit was "
            "reached. Set GITHUB_TOKEN to use an authenticated request."
        )
    elif error.code == 404:
        message = "Repository not found or not publicly accessible. Check owner/name."
    else:
        message = f"GitHub API returned HTTP {error.code}."

    return f"{message} {detail}".strip()


def fetch_open_issues(
    repository: str,
    *,
    limit: int = 100,
    token: str | None = None,
    timeout: float = 15.0,
) -> list[dict[str, Any]]:
    """Fetch up to limit open issues, excluding pull requests.

    Public repositories can be queried without a token. A token is optional and
    should be supplied through the GITHUB_TOKEN environment variable by callers.
    """
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000.")

    full_name = normalize_repository(repository)
    owner, name = full_name.split("/", maxsplit=1)
    page_size = min(100, limit)
    page = 1
    issues: list[dict[str, Any]] = []

    while len(issues) < limit:
        url = (
            f"https://api.github.com/repos/{owner}/{name}/issues"
            f"?state=open&per_page={page_size}&page={page}"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "RepoPilot",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token and token.strip():
            headers["Authorization"] = f"Bearer {token.strip()}"

        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise GitHubAPIError(_error_message(error)) from error
        except (URLError, TimeoutError, OSError) as error:
            raise GitHubAPIError(f"Could not reach the GitHub API: {error}") from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise GitHubAPIError("GitHub returned an invalid JSON response.") from error

        if not isinstance(payload, list):
            raise GitHubAPIError("GitHub returned an unexpected issues response.")

        for item in payload:
            if not isinstance(item, dict) or "pull_request" in item:
                continue

            labels = [
                str(label["name"])
                for label in item.get("labels", [])
                if isinstance(label, dict) and label.get("name")
            ]
            issues.append(
                {
                    "number": item.get("number"),
                    "title": str(item.get("title") or "Untitled"),
                    "body": str(item.get("body") or ""),
                    "labels": labels,
                    "html_url": item.get("html_url"),
                    "state": item.get("state"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                }
            )
            if len(issues) >= limit:
                break

        if len(payload) < page_size:
            break
        page += 1

    return issues[:limit]
