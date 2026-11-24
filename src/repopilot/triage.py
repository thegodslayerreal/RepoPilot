import re

from .rules import DEFAULT_RULES, LabelRule


def _contains_keyword(text: str, keyword: str) -> bool:
    """Match a keyword or phrase without matching it inside a larger word."""
    pattern = rf"(?<!\\w){re.escape(keyword.casefold())}(?!\\w)"
    return re.search(pattern, text) is not None


def suggest_label_details(
    title: str,
    body: str = "",
    rules: tuple[LabelRule, ...] = DEFAULT_RULES,
) -> list[dict[str, str]]:
    """Return label suggestions with the matching keyword that explains each one."""
    text = f"{title}\n{body}".casefold()
    details = []
    for rule in rules:
        matched = next(
            (keyword for keyword in rule.keywords if _contains_keyword(text, keyword)),
            None,
        )
        if matched:
            details.append({"label": rule.label, "reason": f"Matched keyword: {matched}"})
    return details


def suggest_labels(
    title: str,
    body: str = "",
    rules: tuple[LabelRule, ...] = DEFAULT_RULES,
) -> list[str]:
    """Return matching labels in rule order using case-insensitive whole-word rules."""
    return [item["label"] for item in suggest_label_details(title, body, rules)]
