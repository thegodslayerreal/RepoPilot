import re
from itertools import combinations
from typing import Any

_WORDS = re.compile(r"[a-z0-9]+")

def tokens(text: str) -> set[str]:
    return set(_WORDS.findall(text.casefold()))

def jaccard_similarity(left: str, right: str) -> float:
    """Similarity of unique word sets, from 0.0 to 1.0."""
    a, b = tokens(left), tokens(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def find_duplicate_candidates(issues: list[dict[str, Any]], threshold: float = 0.35) -> list[dict[str, Any]]:
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    results = []
    for first, second in combinations(issues, 2):
        a = f"{first.get('title', '')} {first.get('body', '')}"
        b = f"{second.get('title', '')} {second.get('body', '')}"
        score = jaccard_similarity(a, b)
        if score >= threshold:
            results.append({
                "first_number": first.get("number"),
                "second_number": second.get("number"),
                "similarity": round(score, 4),
            })
    return sorted(results, key=lambda item: item["similarity"], reverse=True)
