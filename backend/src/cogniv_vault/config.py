from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_service_key: str = ""

    cors_origins: str = "http://localhost:5173"

    verify_threshold: float = 0.8
    max_attempts: int = 3
    top_k: int = 5

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    groq_model: str = "llama-3.3-70b-versatile"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
