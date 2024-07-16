import time
import json
from typing import Any, TypeVar, Type, Callable
from os import PathLike


T = TypeVar("T")


class RateLimiter:
    def __init__(self, per_second: int):
        """
        レートリミットのクラス

        Args:
            per_second (int): 1回の間隔
        """
        self.per_second = per_second  # リクエスト送信の間隔（秒）
        self.last_called_time = time.time()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.wait()
            response = func(*args, **kwargs)
            self.last_called_time = time.time()
            return response

        return wrapper

    def wait(self):
        elapsed_time = time.time() - self.last_called_time
        if elapsed_time < self.per_second:
            time.sleep(self.per_second - elapsed_time)


class Counter:
    def __init__(self, counter: int, do: Callable) -> None:
        """
        指定の回数呼び出されたときに任意の関数を実行するデコレーター

        Args:
            counter (int): 何回で実行するか
            do (Callable): 実行される関数
        """
        self.count = counter
        self._now = 0
        self.do = do

    def __call__(self, f) -> Any:
        def wrapper(*args, **kwargs):
            self._now += 1
            if self._now == self.count:
                self._now = 0
                self.do()

            resp = f(*args, **kwargs)
            return resp

        return wrapper


def load_from_path(
    path: str | PathLike | T,
    extend: Type[T | None] = type(None),
) -> str | T:
    if not isinstance(path, (str, PathLike, extend)):
        raise TypeError(
            f"Invalid type for path: {type(path)}. Expected str, PathLike, or {extend.__name__}."
        )

    if extend is not None and isinstance(path, extend):
        return path
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_from_json_path(path: str | PathLike) -> dict:
    return json.loads(load_from_path(path))
