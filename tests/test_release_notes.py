from repopilot.release_notes import draft_release_notes


def test_release_notes_categories():
    result = draft_release_notes([
        {"number": 2, "title": "Fix login crash", "labels": ["bug"]},
        {"number": 1, "title": "Add export", "labels": ["feature"]},
    ])
    assert "## Features" in result
    assert "Add export (#1)" in result
    assert "## Bug fixes" in result
    assert "Fix login crash (#2)" in result

def test_empty_release_notes():
    assert draft_release_notes([]) == "# Release notes\n"
