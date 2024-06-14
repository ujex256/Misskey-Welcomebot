import os

from utils import load_from_path


class NGWords:
    """
    NGワードのファイルを読み込む

    initにngワードのテキストファイルのパスを渡してください。
    """
    def __init__(self, path: str | os.PathLike) -> None:
        self.raw = load_from_path(path)
        self._load()

    def __getitem__(self, key) -> set:
        if (key := key.lower()) == "ng":
            return self._ng
        elif key == "excluded":
            return self._allow
        else:
            raise KeyError('"ng"か"excluded"を指定してください')

    def _load(self) -> None:
        data = self.raw.split("\n")
        data = [i.lower() for i in data if i != ""]

        ng = set()
        allow = set()
        for i in data:
            if i[0] == "-":
                allow.add(i[1:].lstrip(" "))
            elif i[0] != "#":
                ng.add(i)
        self._ng = ng
        self._allow = allow

    def match(self, text) -> bool:
        text = text.lower()
        ng = self.all_ng_words
        allow = self.all_excluded_words
        return any(x in text for x in ng) and (not any(x in text for x in allow))

    def why(self, text) -> str | None:
        for i in self.all_ng_words:
            if i in text.lower():
                return i
        return None

    @property
    def all_ng_words(self) -> set:
        return self._ng

    @property
    def all_excluded_words(self) -> set:
        return self._allow
