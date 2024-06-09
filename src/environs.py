from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Literal


class DotenvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Settings(DotenvSettings):
    host: str
    secret_token: str

    db_type: Literal["redis", "pickle"] = "redis"
    db_url: RedisDsn

    config_dir: str = "./config"
    run_server: bool = False
