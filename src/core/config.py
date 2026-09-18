from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentType = Literal["development", "staging", "production", "testing"]


class Settings(BaseSettings):
    app_name: str = Field(
        default="fintech-data-platform", description="Application name"
    )
    environment: EnvironmentType = Field(
        default="development", description="Current environment"
    )
    debug: bool = Field(default=False, description="Debug mode flag")

    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="fintech_ledger")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")

    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_payment_topic: str = Field(default="payments.auth")

    minio_endpoint: str = Field(default="localhost:9000")
    minio_bucket: str = Field(default="fintech-lake")
    minio_secure: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
