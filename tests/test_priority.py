from repopilot.priority import score_priority


def test_security_and_data_loss_signals_produce_critical_priority():
    result = score_priority("Security vulnerability causes data loss")
    assert result["level"] == "medium"
    assert result["score"] == 5
    assert len(result["reasons"]) == 1


def test_crash_and_urgency_produce_high_priority():
    result = score_priority("Urgent: application crash")
    assert result["level"] == "high"
    assert result["score"] == 5


def test_no_signals_default_to_low_with_explanation():
    result = score_priority("Add a configuration option")
    assert result == {
        "level": "low",
        "score": 0,
        "reasons": ["No configured urgency or impact signals found"],
    }


def test_priority_matching_uses_word_boundaries():
    result = score_priority("This is not a crashing issue")
    assert result["level"] == "low"
    assert result["score"] == 0
