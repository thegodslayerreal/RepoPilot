from repopilot.triage import suggest_labels


def test_bug_rule_matches_title_and_body():
    assert "bug" in suggest_labels("App crashes", "It raises an exception")

def test_feature_rule_matches():
    assert suggest_labels("Add dark mode") == ["feature"]

def test_no_match():
    assert suggest_labels("Hello there", "General context") == []
