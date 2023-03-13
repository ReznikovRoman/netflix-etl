from functools import lru_cache

from pydantic import Field
from pydantic.env_settings import BaseSettings


class EnvConfig(BaseSettings.Config):

    @classmethod
    def prepare_field(cls, field) -> None:
        if "env_names" in field.field_info.extra:
            return None
        return super().prepare_field(field)


class Settings(BaseSettings):
    """Project settings."""

    # Elasticsearch
    ES_HOST: str
    ES_PORT: int
    ES_RETRY_ON_TIMEOUT: bool = Field(True)

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DECODE_RESPONSES: bool

    # Postgres
    DB_NAME: str = Field(..., env="NA_DB_NAME")
    DB_USER: str = Field(..., env="NA_DB_USER")
    DB_PASSWORD: str = Field(..., env="NA_DB_PASSWORD")
    DB_HOST: str = Field(..., env="NA_DB_HOST")
    DB_PORT: int = Field(..., env="NA_DB_PORT")

    class Config(EnvConfig):
        env_prefix = "NE_"
        case_sensitive = True


@lru_cache
def get_settings() -> "Settings":
    return Settings()
