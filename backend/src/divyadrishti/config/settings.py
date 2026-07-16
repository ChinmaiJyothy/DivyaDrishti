from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./divyadrishti.db"

    secret_key: str = Field(..., min_length=16)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: list[str] = ["http://localhost:3000"]

    ayanamsa: str = "lahiri"
    house_system: str = "sripati"
    ephemeris_path: str | None = None

    llm_provider: str = "openai"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str | None = None

    # Knowledge Corpus / semantic retrieval
    embedding_provider: str = "sentence_transformers"
    embedding_model: str | None = None
    corpus_vector_store_dir: str = ".chroma"
    corpus_min_rule_confidence: float = 0.35

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                value = value[1:-1]
            return [
                origin.strip().strip('"').strip("'")
                for origin in value.split(",")
                if origin.strip()
            ]
        return value

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
