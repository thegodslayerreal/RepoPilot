import re

from .rules import DEFAULT_RULES, LabelRule


def _contains_keyword(text: str, keyword: str) -> bool:
    """Match a keyword or phrase without matching it inside a larger word."""
    pattern = rf"(?<!\w){re.escape(keyword.casefold())}(?!\w)"
    return re.search(pattern, text) is not None


def suggest_labels(
    title: str,
    body: str = "",
    rules: tuple[LabelRule, ...] = DEFAULT_RULES,
) -> list[str]:
    """Return matching labels in rule order using case-insensitive whole-word rules."""
    text = f"{title}\n{body}".casefold()

    return [
        rule.label
        for rule in rules
        if any(_contains_keyword(text, keyword) for keyword in rule.keywords)
    ]
