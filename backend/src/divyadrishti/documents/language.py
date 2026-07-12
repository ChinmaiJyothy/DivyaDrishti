"""Language detection and translation for multilingual documents."""

from abc import ABC, abstractmethod
from pathlib import Path


class LanguageDetector:
    """Detect language from text using langdetect."""

    def detect(self, text: str) -> str:
        try:
            from langdetect import detect
        except ImportError as exc:
            raise ImportError("langdetect is required for language detection.") from exc

        if not text.strip():
            return "unknown"

        try:
            return detect(text[:2000])
        except Exception:
            return "unknown"


class TranslatorProvider(ABC):
    """Abstract base for translators."""

    @abstractmethod
    def translate(self, text: str, target_lang: str = "en") -> str:
        """Translate text to the target language."""


class DeepTranslatorProvider(TranslatorProvider):
    """Translate text using deep-translator (Google Translate).

    The original text is always preserved; translation is optional.
    """

    def __init__(self, source_lang: str = "auto", target_lang: str = "en") -> None:
        self.source_lang = source_lang
        self.target_lang = target_lang

    def translate(self, text: str, target_lang: str = "en") -> str:
        try:
            from deep_translator import GoogleTranslator
        except ImportError as exc:
            raise ImportError("deep-translator is required for translation.") from exc

        if not text.strip():
            return text

        translator = GoogleTranslator(source=self.source_lang, target=target_lang or self.target_lang)
        try:
            return translator.translate(text)
        except Exception:
            return text


class IdentityTranslator(TranslatorProvider):
    """No-op translator for environments without translation support."""

    def translate(self, text: str, target_lang: str = "en") -> str:
        return text
