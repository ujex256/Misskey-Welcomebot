# pyright: reportCallIssue=false
import pytest
from pydantic import ValidationError
from typing import Type

from environs import Settings


default_kwargs = {
    "_env_file": None,  # Don't load .env file
    "host": "dummy",
    "secret_token": "dummy",
    "db_type": "pickle",
}


def test_required():
    with pytest.raises(ValidationError) as e:
        Settings(_env_file=None)
        assert e.value.error_count() == 2
        assert [i["loc"][0] for i in e.value.errors()] == ["host", "secret_token"]


@pytest.mark.parametrize(
    "url, exp",
    [
        [None, ValueError],
        ["non-redis-url", ValidationError],
        ["redis://localhost:6379", None],
    ],
)
def test_redis_db(url: str | None, exp: Type[Exception] | None):
    kwargs = default_kwargs.copy()
    kwargs["db_type"] = "redis"
    kwargs["db_url"] = url
    if exp is not None:
        with pytest.raises(exp):
            Settings(**kwargs)
    else:
        Settings(**kwargs)


@pytest.mark.parametrize(
    "ip, raise_exp",
    [
        ["", True],
        ["0.0.0.0", False],
        ["255.255.255.255", False],
        ["255.255.255.256", True],
    ],
)
def test_server_host(ip: str, raise_exp: bool):
    kwargs = default_kwargs.copy()
    kwargs["server_host"] = ip
    if raise_exp:
        with pytest.raises(ValidationError):
            Settings(**kwargs)
    else:
        Settings(**kwargs)
