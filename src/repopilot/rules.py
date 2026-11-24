from dataclasses import dataclass


@dataclass(frozen=True)
class LabelRule:
    label: str
    keywords: tuple[str, ...]

DEFAULT_RULES = (
    LabelRule("bug", ("bug", "crash", "error", "exception", "broken", "fail")),
    LabelRule("feature", ("feature", "add", "support", "implement", "enhancement")),
    LabelRule("documentation", ("docs", "documentation", "readme", "typo", "guide")),
    LabelRule("question", ("question", "how do i", "how can i", "help", "why does")),
    LabelRule("performance", ("slow", "performance", "memory leak", "latency", "timeout")),
)
