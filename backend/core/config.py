from functools import lru_cache
from pydantic import SecretStr, AmqpDsn, RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: PostgresDsn

    rabbitmq_url: AmqpDsn
    task_queue: str = "task_queue"

    redis_url: RedisDsn
    redis_items_key: str = "items"

    secret_key: SecretStr
    debug: bool

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    cached settings factory
    """

    return Settings()  # type: ignore


settings = get_settings()
