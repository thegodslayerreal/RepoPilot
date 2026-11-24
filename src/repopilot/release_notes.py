from collections import defaultdict
from typing import Any

ORDER = ("breaking-change", "feature", "bug", "documentation", "other")
HEADINGS = {
    "breaking-change": "Breaking changes",
    "feature": "Features",
    "bug": "Bug fixes",
    "documentation": "Documentation",
    "other": "Other changes",
}

def draft_release_notes(pulls: list[dict[str, Any]]) -> str:
    groups = defaultdict(list)
    for pull in pulls:
        labels = {str(label).casefold() for label in pull.get("labels", [])}
        category = next((name for name in ORDER[:-1] if name in labels), "other")
        groups[category].append(pull)

    lines = ["# Release notes", ""]
    for category in ORDER:
        entries = groups.get(category, [])
        if not entries:
            continue
        lines.extend([f"## {HEADINGS[category]}", ""])
        for pull in sorted(entries, key=lambda item: int(item.get("number", 0))):
            number = pull.get("number")
            suffix = f" (#{number})" if number is not None else ""
            lines.append(f"- {str(pull.get('title', 'Untitled')).strip()}{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
