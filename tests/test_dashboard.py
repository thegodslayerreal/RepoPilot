import json

from repopilot.dashboard import render_dashboard


def sample_report():
    return {
        "repository": "octo/project",
        "generated_at": "2026-11-25T10:00:00+00:00",
        "summary": {
            "issues_analyzed": 2,
            "issues_with_suggested_labels": 1,
            "potential_duplicate_pairs": 1,
        },
        "issues": [
            {
                "number": 1,
                "title": "Add docs",
                "url": "https://github.com/octo/project/issues/1",
                "state": "open",
                "labels": [],
                "suggested_labels": ["documentation"],
            },
            {
                "number": 2,
                "title": "Crash on startup",
                "url": "https://github.com/octo/project/issues/2",
                "state": "open",
                "labels": ["bug"],
                "suggested_labels": [],
            },
        ],
        "duplicate_candidates": [
            {"first_number": 1, "second_number": 2, "similarity": 0.42}
        ],
    }


def test_render_dashboard_contains_report_data_and_dashboard_sections():
    html = render_dashboard(sample_report())

    assert "RepoPilot" in html
    assert "octo/project" in html
    assert "Suggested label distribution" in html
    assert "Potential duplicate issues" in html
    assert "documentation" in html
    assert "issue-rows" in html
    assert "Search issues or labels" in html


def test_render_dashboard_escapes_script_terminators_in_untrusted_issue_text():
    report = sample_report()
    report["issues"][0]["title"] = '</script><script>alert("xss")</script>'

    html = render_dashboard(report)

    assert '</script><script>alert("xss")</script>' not in html
    assert r"\u003c/script\u003e" in html
    assert json.loads(
        html.split('<script id="report-data" type="application/json">', 1)[1]
        .split("</script>", 1)[0]
    )["issues"][0]["title"] == '</script><script>alert("xss")</script>'
