"""Combine RepoPilot's local issue checks into a JSON-ready report."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .github_client import normalize_repository
from .similarity import find_duplicate_candidates
from .triage import suggest_labels


def build_analysis_report(
    repository: str,
    issues: list[dict[str, Any]],
    threshold: float = 0.35,
) -> dict[str, Any]:
    """Build a report without modifying the source repository or its issues."""
    full_name = normalize_repository(repository)
    analyzed_issues: list[dict[str, Any]] = []
    duplicate_input: list[dict[str, Any]] = []

    for issue in issues:
        title = str(issue.get("title") or "Untitled")
        body = str(issue.get("body") or "")
        labels = [str(label) for label in issue.get("labels", [])]
        suggestions = suggest_labels(title, body)

        analyzed_issues.append(
            {
                "number": issue.get("number"),
                "title": title,
                "url": issue.get("html_url"),
                "state": issue.get("state", "open"),
                "labels": labels,
                "suggested_labels": suggestions,
            }
        )
        duplicate_input.append(
            {
                "number": issue.get("number"),
                "title": title,
                "body": body,
            }
        )

    duplicates = find_duplicate_candidates(duplicate_input, threshold)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    return {
        "repository": full_name,
        "generated_at": generated_at,
        "summary": {
            "issues_analyzed": len(analyzed_issues),
            "issues_with_suggested_labels": sum(
                bool(issue["suggested_labels"]) for issue in analyzed_issues
            ),
            "potential_duplicate_pairs": len(duplicates),
        },
        "issues": analyzed_issues,
        "duplicate_candidates": duplicates,
    }
