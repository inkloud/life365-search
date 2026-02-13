from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "life365-search"
    environment: str = "local"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    opensearch_host: str = "http://opensearch:9200"
    opensearch_user: str | None = None
    opensearch_password: str | None = None
    opensearch_index_prefix: str = "products"

    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"

    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
