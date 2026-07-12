"""Multilingual support for the AI Conversation Engine."""

from abc import ABC, abstractmethod


SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "te": "Telugu",
    "ta": "Tamil",
    "ml": "Malayalam",
    "gu": "Gujarati",
    "mr": "Marathi",
}


class Translator(ABC):
    """Abstract translator for response localization."""

    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        """Translate text to the target language."""


class DeepTranslator(Translator):
    """Translator using deep-translator (Google Translate)."""

    def translate(self, text: str, target_lang: str) -> str:
        try:
            from deep_translator import GoogleTranslator
        except ImportError as exc:
            raise ImportError("deep-translator is required for DeepTranslator.") from exc

        if target_lang not in SUPPORTED_LANGUAGES:
            return text

        target = "en" if target_lang == "en" else target_lang
        try:
            return GoogleTranslator(source="auto", target=target).translate(text)
        except Exception:
            return text


class MockTranslator(Translator):
    """No-op translator for testing and environments without translation."""

    def translate(self, text: str, target_lang: str) -> str:
        return text


class LanguageService:
    """Manage language detection and translation."""

    def __init__(self, translator: Translator | None = None) -> None:
        self.translator = translator or MockTranslator()

    def localize(self, text: str, target_lang: str) -> str:
        """Return text in the target language if supported."""
        if target_lang == "en" or target_lang not in SUPPORTED_LANGUAGES:
            return text
        return self.translator.translate(text, target_lang)

    def is_supported(self, language: str) -> bool:
        """Return True if the language is supported."""
        return language in SUPPORTED_LANGUAGES
