import pytest

from repopilot.analysis import build_analysis_report


def test_analysis_report_includes_suggestions_and_duplicate_candidates():
    issues = [
        {
            "number": 1,
            "title": "App crashes on startup",
            "body": "Windows launch crash",
            "labels": [],
            "html_url": "https://github.com/octo/project/issues/1",
        },
        {
            "number": 2,
            "title": "Startup crash on Windows",
            "body": "App crashes during launch",
            "labels": ["bug"],
            "html_url": "https://github.com/octo/project/issues/2",
        },
        {
            "number": 3,
            "title": "Add dark theme",
            "body": "New appearance option",
            "labels": [],
            "html_url": "https://github.com/octo/project/issues/3",
        },
    ]

    report = build_analysis_report("https://github.com/octo/project", issues, 0.2)

    assert report["repository"] == "octo/project"
    assert report["summary"]["issues_analyzed"] == 3
    assert report["summary"]["issues_with_suggested_labels"] == 3
    assert report["issues"][0]["suggested_labels"] == ["bug"]
    assert report["issues"][2]["suggested_labels"] == ["feature"]
    assert report["duplicate_candidates"]
    assert report["duplicate_candidates"][0]["first_number"] == 1
    assert report["duplicate_candidates"][0]["second_number"] == 2


def test_analysis_report_rejects_invalid_duplicate_threshold():
    with pytest.raises(ValueError, match="threshold"):
        build_analysis_report("octo/project", [], 1.5)
