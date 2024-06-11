from pathlib import Path
from typing import Literal, Optional

from pydantic import DirectoryPath, RedisDsn, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DotenvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class Settings(DotenvSettings):
    host: str = Field(default=...)
    secret_token: str = Field(default=...)

    db_type: Literal["redis", "pickle"] = "redis"
    db_url: Optional[RedisDsn] = None

    config_dir: DirectoryPath = Path("./config")
    run_server: bool = False

    @model_validator(mode="after")
    def required_when_redis(self):
        if self.db_url is None and self.db_type == "redis":
            raise ValueError("DB_URL is required when DB_TYPE is redis")
        return self
