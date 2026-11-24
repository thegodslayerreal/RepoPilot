from dataclasses import dataclass


@dataclass(frozen=True)
class LabelRule:
    label: str
    keywords: tuple[str, ...]


DEFAULT_RULES = (
    LabelRule("bug", ("bug", "crash", "error", "exception", "broken", "fail")),
    # Avoid generic verbs such as "add", which also appear in documentation requests.
    LabelRule(
        "feature",
        ("feature", "support", "implement", "enhancement", "introduce", "provide"),
    ),
    LabelRule(
        "documentation",
        ("docs", "documentation", "readme", "typo", "guide", "hosting platforms"),
    ),
    LabelRule("question", ("question", "how do i", "how can i", "help", "why does")),
    LabelRule("performance", ("slow", "performance", "memory leak", "latency", "timeout")),
)
