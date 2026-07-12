from divyadrishti.ai import SafetyGuard


def test_safety_guard_flags_disallowed_content():
    guard = SafetyGuard()
    safe, flagged = guard.check_input("You should take this medication")
    assert not safe
    assert "medical_advice" in flagged


def test_safety_guard_sanitizes_certainty():
    guard = SafetyGuard()
    text = guard.sanitize("You will definitely get married next year.")
    assert "may" in text.lower()
