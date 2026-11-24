from repopilot.triage import suggest_labels


def test_bug_rule_matches_title_and_body():
    assert "bug" in suggest_labels("App crashes", "It raises an exception")


def test_feature_rule_matches_specific_feature_language():
    assert suggest_labels("Implement dark mode") == ["feature"]


def test_documentation_request_is_not_misclassified_as_feature():
    assert suggest_labels(
        "Add Cloudflare to Flask Hosting Platforms docs?",
        "Add a link to the deployment guide.",
    ) == ["documentation"]


def test_no_match():
    assert suggest_labels("Hello there", "General context") == []
