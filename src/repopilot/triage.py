from .rules import DEFAULT_RULES, LabelRule

def suggest_labels(title: str, body: str = "", rules: tuple[LabelRule, ...] = DEFAULT_RULES) -> list[str]:
    """Return matching labels in rule order using case-insensitive keyword rules."""
    text = f"{title}\n{body}".casefold()
    return [
        rule.label for rule in rules
        if any(keyword.casefold() in text for keyword in rule.keywords)
    ]
