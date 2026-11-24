"""Read-only repository health metrics derived from open issues."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_health_report(
    issues: list[dict[str, Any]],
    *,
    stale_days: int = 30,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Summarize issue age, inactivity, assignment, and stale work.

    An issue is stale when it has not been updated for at least stale_days.
    Missing or invalid timestamps are counted separately, not treated as stale.
    """
    if stale_days < 1:
        raise ValueError("stale_days must be at least 1.")

    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    stale_issues: list[dict[str, Any]] = []
    age_buckets = {"under_7_days": 0, "7_to_30_days": 0, "30_to_90_days": 0, "over_90_days": 0}
    missing_created = 0
    missing_updated = 0
    unassigned = 0
    total_age_days = 0
    age_count = 0

    for issue in issues:
        created = _parse_timestamp(issue.get("created_at"))
        updated = _parse_timestamp(issue.get("updated_at"))

        if not issue.get("assignees"):
            unassigned += 1

        if created is None:
            missing_created += 1
        else:
            age_days = max(0, (now - created).days)
            total_age_days += age_days
            age_count += 1
            if age_days < 7:
                age_buckets["under_7_days"] += 1
            elif age_days < 30:
                age_buckets["7_to_30_days"] += 1
            elif age_days < 90:
                age_buckets["30_to_90_days"] += 1
            else:
                age_buckets["over_90_days"] += 1

        if updated is None:
            missing_updated += 1
            continue

        inactive_days = max(0, (now - updated).days)
        if inactive_days >= stale_days:
            stale_issues.append(
                {
                    "number": issue.get("number"),
                    "title": str(issue.get("title") or "Untitled"),
                    "url": issue.get("html_url"),
                    "inactive_days": inactive_days,
                }
            )

    stale_issues.sort(key=lambda item: item["inactive_days"], reverse=True)
    return {
        "stale_days_threshold": stale_days,
        "issues_checked": len(issues),
        "stale_issue_count": len(stale_issues),
        "stale_issue_percentage": round(len(stale_issues) / len(issues) * 100, 1)
        if issues
        else 0.0,
        "unassigned_issue_count": unassigned,
        "average_issue_age_days": round(total_age_days / age_count, 1) if age_count else None,
        "issue_age_buckets": age_buckets,
        "missing_created_at_count": missing_created,
        "missing_updated_at_count": missing_updated,
        "stale_issues": stale_issues,
    }
