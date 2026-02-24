from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    RABBITMQ_URL: str = ""
    REDIS_URL: str = ""
    SECRET_KEY: str = ""
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8", extra="ignore")

settings = Settings()