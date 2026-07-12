"""Safety guard for the AI Conversation Engine."""

import re


class SafetyGuard:
    """Filter disallowed content and add warnings to responses."""

    DISALLOWED_PATTERNS = {
        "medical_advice": re.compile(r"\b(treat|cure|diagnose|medication|doctor|prescription)\b", re.IGNORECASE),
        "legal_advice": re.compile(r"\b(lawsuit|sue|legal action|court|lawyer|legal case)\b", re.IGNORECASE),
        "financial_guarantee": re.compile(r"\b(guarantee|guaranteed profit|will make money|sure gain)\b", re.IGNORECASE),
        "fear_based": re.compile(r"\b(disaster|dangerous|terrible|calamity|death|fatal)\b", re.IGNORECASE),
    }

    def check_input(self, text: str) -> tuple[bool, list[str]]:
        """Return (is_safe, flagged_categories)."""
        flagged = [name for name, pattern in self.DISALLOWED_PATTERNS.items() if pattern.search(text)]
        return not flagged, flagged

    def check_output(self, text: str) -> str:
        """Return text or a warning if disallowed content is detected."""
        safe, flagged = self.check_input(text)
        if safe:
            return text

        warning = (
            "\n\n[Note: This response may contain content that could be interpreted as "
            + ", ".join(flagged)
            + ". Astrological insights are interpretive, not professional advice.]"
        )
        return text + warning

    def sanitize(self, text: str) -> str:
        """Remove deterministic certainty language and replace with tentative phrasing."""
        text = re.sub(r"\b(will definitely|will certainly|guaranteed to|must|will)\b", "may", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(you must|you should always|you have to)\b", "you might consider", text, flags=re.IGNORECASE)
        return text
