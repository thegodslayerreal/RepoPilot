from datetime import datetime, timezone
import pytest

from repopilot.health import build_health_report


AS_OF = datetime(2026, 11, 25, tzinfo=timezone.utc)


def test_health_report_counts_stale_unassigned_and_age_buckets():
    issues = [
        {
            "number": 1,
            "title": "Old issue",
            "html_url": "https://github.com/octo/project/issues/1",
            "created_at": "2026-07-01T00:00:00Z",
            "updated_at": "2026-08-01T00:00:00Z",
            "assignees": [],
        },
        {
            "number": 2,
            "title": "Recent issue",
            "created_at": "2026-11-20T00:00:00Z",
            "updated_at": "2026-11-24T00:00:00Z",
            "assignees": ["maintainer"],
        },
    ]

    report = build_health_report(issues, stale_days=30, as_of=AS_OF)

    assert report["issues_checked"] == 2
    assert report["stale_issue_count"] == 1
    assert report["stale_issues"][0]["number"] == 1
    assert report["unassigned_issue_count"] == 1
    assert report["issue_age_buckets"]["over_90_days"] == 1
    assert report["issue_age_buckets"]["under_7_days"] == 1
    assert report["average_issue_age_days"] == 76.0


def test_health_report_handles_missing_and_invalid_timestamps():
    report = build_health_report(
        [{"number": 3, "created_at": "not-a-date", "updated_at": None}],
        as_of=AS_OF,
    )

    assert report["missing_created_at_count"] == 1
    assert report["missing_updated_at_count"] == 1
    assert report["stale_issue_count"] == 0
    assert report["average_issue_age_days"] is None


def test_health_report_rejects_invalid_stale_threshold():
    with pytest.raises(ValueError, match="stale_days"):
        build_health_report([], stale_days=0, as_of=AS_OF)
