import pathlib


class NGWords:
    """
    NGワードのファイルを読み込む

    initにngワードのテキストファイルのパスを渡してください。
    """
    def __init__(self, path) -> None:
        self._path = pathlib.Path(path)
        self._load()

    def __getitem__(self, key) -> dict:
        if (key := key.lower()) == "ng":
            return self._ng
        elif key == "excluded":
            return self._allow
        else:
            raise KeyError('"ng"か"excluded"を指定してください')

    def _load(self) -> None:
        with self._path.open() as f:
            data = f.read().split("\n")
        data = [j.lower() for j in data if j != ""]
        self._ng = {j for j in data if (j[0] != "-") and (j[0] != "#")}
        self._allow = {j[1:] for j in data if j[0] == "-"}

    def match(self, text) -> bool:
        text = text.lower()
        ng = self.all_ng_words
        allow = self.all_excluded_words
        return any(x in text for x in ng) and (not any(x in text for x in allow))

    def why(self, text) -> str | None:
        for i in self.all_ng_words:
            if i in text:
                return i
        return None

    @property
    def all_ng_words(self) -> set:
        return self._ng

    @property
    def all_excluded_words(self) -> set:
        return self._allow


if __name__ == "__main__":
    print(NGWords(r"ng_words/ngWords.txt").match("r-18"))
    print(NGWords(r"ngWords_Hiraassssssss.txt").all_ng_words)  # FileNotFound
