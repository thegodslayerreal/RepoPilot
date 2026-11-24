"""Transparent, advisory issue-priority scoring."""


# Each signal contributes points once, even if it appears repeatedly.
# Severe security and data-integrity risks are critical on their own.
_PRIORITY_SIGNALS = (
    (7, ("remote code execution", "security vulnerability", "data loss", "data corruption")),
    (3, ("production outage", "crash", "regression", "blocking", "blocks release")),
    (2, ("urgent", "asap", "release blocker", "cannot use", "can't use")),
    (1, ("all users", "every request", "all requests", "affects everyone")),
)


def _contains_signal(text: str, signal: str) -> bool:
    """Match a phrase without treating it as part of a larger word."""
    start = 0
    while (index := text.find(signal, start)) != -1:
        end = index + len(signal)
        left_is_word = index > 0 and (text[index - 1].isalnum() or text[index - 1] == "_")
        right_is_word = end < len(text) and (text[end].isalnum() or text[end] == "_")
        if not left_is_word and not right_is_word:
            return True
        start = index + 1
    return False


def score_priority(title: str, body: str = "") -> dict[str, object]:
    """Score explicit impact and urgency language, returning reasons for the score.

    This heuristic is advisory, not a substitute for maintainer assessment.
    """
    text = f"{title}\n{body}".casefold()
    score = 0
    reasons: list[str] = []

    for points, signals in _PRIORITY_SIGNALS:
        matched = next((signal for signal in signals if _contains_signal(text, signal)), None)
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
