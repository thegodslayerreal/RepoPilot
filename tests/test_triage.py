from repopilot.triage import suggest_label_details, suggest_labels


def test_bug_rule_matches_title_and_body():
    assert "bug" in suggest_labels("App crashes", "It raises an exception")


def test_feature_rule_matches_specific_feature_language():
    assert suggest_labels("Implement dark mode") == ["feature"]


def test_documentation_request_is_not_misclassified_as_feature():
    title = "Add Cloudflare to Flask Hosting Platforms docs?"
    body = (
        "Cloudflare workers supports deploying Flask applications. "
        "Could we add a link to this page to the Hosting Platforms section of the docs?"
    )
    assert suggest_labels(title, body) == ["documentation"]


def test_keyword_matching_does_not_match_inside_larger_words():
    assert "feature" not in suggest_labels(
        "Add deployment documentation",
        "This service supports deploying Flask applications.",
    )


def test_no_match():
    assert suggest_labels("Hello there", "General context") == []


def test_label_explanations_identify_the_matching_keyword():
    assert suggest_label_details("Application crashes") == [
        {"label": "bug", "reason": "Matched keyword: crash"}
    ]
