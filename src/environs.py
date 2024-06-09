from pathlib import Path
from typing import Literal

from pydantic import DirectoryPath, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DotenvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Settings(DotenvSettings):
    host: str
    secret_token: str

    db_type: Literal["redis", "pickle"] = "redis"
    db_url: RedisDsn

    config_dir: DirectoryPath = Path("./config")
    run_server: bool = False
