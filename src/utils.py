import json
from os import PathLike
from typing import Any, Callable, Type, TypeVar

T = TypeVar("T")


class Counter:
    def __init__(self, count: int, do: Callable) -> None:
        """
        指定の回数呼び出されたときに任意の関数を実行するデコレーター

        Args:
            counter (int): 何回で実行するか
            do (Callable): 実行される関数
        """
        self.count = count
        self.do = do
        self._now = 0

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
            f"Invalid type for path: {type(path)}. "
            f"Expected str, PathLike, or {extend.__name__}."
        )

    if extend is not None and isinstance(path, extend):
        return path
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_from_json_path(path: str | PathLike) -> dict:
    return json.loads(load_from_path(path))


def can_renote(note: dict) -> bool:
    """リノート可能か判定する(ノート数はカウントしていないので注意)

    Args:
        note (dict): misskeyのノート

    Returns:
        bool: 可能か
    """
    is_public = note["visibility"] == "public"
    text_exists = note["text"] is not None
    is_reply = note["replyId"] is not None
    return is_public and text_exists and not is_reply


def can_reply(note: dict, username: str) -> bool:
    """リプライ可能(pingノート)か判定

    Args:
        note (dict): misskeyのノート

    Returns:
        bool: リプライ可能か
    """
    if note["text"] is None:
        return False
    is_ping = "/ping" in note["text"]
    is_mention = f"@{username}" in note["text"]
    is_specified = note["visibility"] == "specified"
    return is_ping and (is_mention or is_specified)
