from repopilot.priority import score_priority


def test_security_and_data_loss_signals_produce_critical_priority():
    result = score_priority("Security vulnerability causes a crash")
    assert result["level"] == "critical"
    assert result["score"] == 10
    assert len(result["reasons"]) == 2


def test_each_severe_signal_is_critical_on_its_own():
    for signal in ("remote code execution", "security vulnerability", "data loss", "data corruption"):
        result = score_priority(f"Report: {signal}")
        assert result["level"] == "critical"
        assert result["score"] == 7


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


def test_priority_matching_uses_word_boundaries_and_punctuation():
    assert score_priority("This is not a crashing issue")["score"] == 0
    assert score_priority("SECURITY VULNERABILITY: exposed endpoint")["level"] == "critical"
    assert score_priority("No crashlooping behavior")["score"] == 0
