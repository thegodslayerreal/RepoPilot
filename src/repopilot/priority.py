"""Transparent, advisory issue-priority scoring."""

from __future__ import annotations

import re


# Each signal contributes points once, even if it appears repeatedly.
_PRIORITY_SIGNALS = (
    (5, ("remote code execution", "security vulnerability", "data loss", "data corruption")),
    (3, ("production outage", "crash", "regression", "blocking", "blocks release")),
    (2, ("urgent", "asap", "release blocker", "cannot use", "can't use")),
    (1, ("all users", "every request", "all requests", "affects everyone")),
)


def score_priority(title: str, body: str = "") -> dict[str, object]:
    """Score explicit impact and urgency language, returning reasons for the score.

    This heuristic is advisory, not a substitute for maintainer assessment.
    """
    text = f"{title}\n{body}".casefold()
    score = 0
    reasons: list[str] = []

    for points, signals in _PRIORITY_SIGNALS:
        matched = next(
            (
                signal
                for signal in signals
                if re.search(rf"(?<!\w){re.escape(signal)}(?!\w)", text)
            ),
            None,
        )
        if matched:
            score += points
            reasons.append(f"+{points}: matched '{matched}'")

    score = min(score, 10)
    if score >= 7:
        level = "critical"
    elif score >= 4:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"

    if not reasons:
        reasons.append("No configured urgency or impact signals found")

    return {"level": level, "score": score, "reasons": reasons}
