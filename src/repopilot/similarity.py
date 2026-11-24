import pytest

from repopilot.similarity import (
    find_duplicate_candidates,
    jaccard_similarity,
)


def test_jaccard_score():
    assert jaccard_similarity("red blue green", "red blue") == pytest.approx(
        2 / 3
    )


def test_empty_inputs():
    assert jaccard_similarity("", "") == 1.0


def test_candidates_are_sorted():
    issues = [
        {
            "number": 1,
            "title": "App crashes on startup",
            "body": "Windows launch crash",
        },
        {
            "number": 2,
            "title": "Startup crash",
            "body": "App crashes on Windows",
        },
        {
            "number": 3,
            "title": "Add dark theme",
            "body": "New appearance option",
        },
    ]

    result = find_duplicate_candidates(issues, 0.2)

    assert result
    assert result[0]["similarity"] >= result[-1]["similarity"]


def test_threshold_validation():
    with pytest.raises(ValueError):
        find_duplicate_candidates([], 1.5)
