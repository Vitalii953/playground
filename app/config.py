from pydantic.config import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/sandbox_db"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq/"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "dev_secret_key_123"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()