"""Conversation memory for the AI Conversation Engine."""

from typing import Any


class ConversationMemory:
    """In-memory conversation memory with user preferences."""

    def __init__(self, max_history: int = 20) -> None:
        self.history: list[dict[str, str]] = []
        self.preferences: dict[str, Any] = {}
        self.max_history = max_history

    def add_exchange(self, user_message: str, assistant_message: str) -> None:
        """Add a user/assistant exchange to the conversation history."""
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2 :]

    def get_history(self) -> list[dict[str, str]]:
        """Return the current conversation history."""
        return self.history

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference."""
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Return a user preference."""
        return self.preferences.get(key, default)

    def summary(self) -> dict[str, Any]:
        """Return a summary for prompt context."""
        return {
            "preferred_language": self.get_preference("language", "en"),
            "explanation_depth": self.get_preference("explanation_depth", "balanced"),
            "frequently_discussed_topics": self.get_preference("topics", []),
        }
