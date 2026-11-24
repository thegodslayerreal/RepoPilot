import json
from io import BytesIO
from urllib.error import HTTPError
from unittest.mock import patch

import pytest

from repopilot.github_client import (
    GitHubAPIError,
    fetch_open_issues,
    normalize_repository,
)


class FakeResponse:
    def __init__(self, payload):
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.body


def test_normalize_repository_names_and_urls():
    assert normalize_repository("octo/project") == "octo/project"
    assert normalize_repository("https://github.com/octo/project.git") == "octo/project"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "octo",
        "octo/project/issues/1",
        "https://example.com/octo/project",
        "https://github.com/octo/project/issues/1",
        "octo/../project",
    ],
)
def test_normalize_repository_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        normalize_repository(value)


def test_fetch_open_issues_paginates_filters_pull_requests_and_uses_token():
    first_page = [
        {"number": 1, "title": "Bug one", "body": "Details", "labels": [{"name": "bug"}]},
        {"number": 2, "title": "Bug two", "body": "", "labels": []},
        {"number": 3, "title": "Bug three", "body": "", "labels": []},
        {
            "number": 50,
            "title": "A pull request",
            "body": "",
            "labels": [],
            "pull_request": {"url": "https://api.github.com/pulls/50"},
        },
    ]
    second_page = [
        {"number": 4, "title": "Bug four", "body": None, "labels": [{"name": "regression"}]}
    ]

    with patch(
        "repopilot.github_client.urlopen",
        side_effect=[FakeResponse(first_page), FakeResponse(second_page)],
    ) as mocked_urlopen:
        issues = fetch_open_issues(
            "octo/project",
            limit=4,
            token="example-token",
        )

    assert [issue["number"] for issue in issues] == [1, 2, 3, 4]
    assert issues[0]["labels"] == ["bug"]
    assert issues[3]["body"] == ""
    assert mocked_urlopen.call_count == 2
    first_request = mocked_urlopen.call_args_list[0].args[0]
    assert first_request.get_header("Authorization") == "Bearer example-token"
    assert "page=2" in mocked_urlopen.call_args_list[1].args[0].full_url


def test_fetch_open_issues_rejects_invalid_limit():
    with pytest.raises(ValueError, match="between 1 and 1000"):
        fetch_open_issues("octo/project", limit=0)


def test_fetch_open_issues_explains_not_found():
    error = HTTPError(
        "https://api.github.com/repos/octo/missing/issues",
        404,
        "Not Found",
        hdrs=None,
        fp=BytesIO(b'{"message":"Not Found"}'),
    )
    with patch("repopilot.github_client.urlopen", side_effect=error):
        with pytest.raises(GitHubAPIError, match="not found"):
            fetch_open_issues("octo/missing")
