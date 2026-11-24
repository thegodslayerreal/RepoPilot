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
                "label_explanations": [{"label": "documentation", "reason": "Matched keyword: docs"}],
                "priority": "medium",
                "priority_score": 2,
                "priority_reasons": ["+2: matched 'urgent'"],
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
        "health": {
            "stale_issue_count": 1,
            "unassigned_issue_count": 1,
            "average_issue_age_days": 76.0,
            "issue_age_buckets": {
                "under_7_days": 0,
                "7_to_30_days": 0,
                "30_to_90_days": 1,
                "over_90_days": 1,
            },
        },
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
    assert "<th>Priority</th>" in html
    assert "priority-medium" in html
    assert "Matched keyword: docs" in html
    assert 'id="health-panel"' in html
    assert 'id="stale-issue-count"' in html
    assert 'id="unassigned-issue-count"' in html
    assert 'id="average-issue-age"' in html
    assert 'id="issue-age-buckets"' in html
    assert 'health.stale_issue_count ?? 0' in html


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



def test_dashboard_validates_external_urls_and_links_duplicate_candidates():
    html = render_dashboard(sample_report())

    assert 'parsed.protocol === "https:" || parsed.protocol === "http:"' in html
    assert 'link.href = safeUrl' in html
    assert 'link.rel = "noopener noreferrer"' in html
    assert 'line.append(issueLink(first' in html
    assert 'line.append(issueLink(second' in html
    assert 'link.href=issue.url' not in html


def test_dashboard_does_not_trust_javascript_issue_urls():
    report = sample_report()
    report["issues"][0]["url"] = "javascript:alert(1)"

    html = render_dashboard(report)

    assert "function safeExternalUrl(value)" in html
    assert 'parsed.protocol === "https:" || parsed.protocol === "http:"' in html
    assert 'link.href=issue.url' not in html
