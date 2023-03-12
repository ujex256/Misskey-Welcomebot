import pathlib
import os

class NGWords:
    """
    NGワードのファイルを読み込む

    ngWords.txt
    ngWords_Hira.txt
    ngWords_Kana.txt
    ngWords_Romaji.txt
    の4つが必要

    initに渡す名前はngWords.txt(ベース)です。
    """

    DEFAULT_NAME = "ngWords.txt"
    FILENAMES = ["ngWords.txt", "ngWords_Hira.txt", "ngWords_Kana.txt", "ngWords_Romaji.txt"]
    def __init__(self, path) -> None:
        self._path = pathlib.Path(path)
        if self._path.name != self.DEFAULT_NAME:
            self.set_default_name(self._path.name)
        self._ng = {"base": {}, "hira": {}, "kana": {}, "romaji": {}}
        self._allow = self._ng.copy()
        self._initialize_words_dict()

    def __getitem__(self, key) -> dict:
        if (key := key.lower()) == "ng":
            return self._ng
        elif key == "excluded":
            return self._allow
        else: raise KeyError('"ng"か"excluded"を指定してください')

    @classmethod
    def set_default_name(cls, name: str) -> list:
        cls.DEFAULT_NAME = name
        cls.FILENAMES = [name]
        types = ["Hira", "Kana", "Romaji"]
        s = list(os.path.splitext(name))
        for i in types:
            cls.FILENAMES.append(f"{s[0]}_{i}{s[1]}")
        return cls.FILENAMES

    def _initialize_words_dict(self) -> None:
        keys = list(self._ng.keys())
        for i in range(4):
            with self._path.parent.joinpath(self.FILENAMES[i]).open(encoding="utf8") as f:
                data = f.read().split("\n")
            data = [i for i in data if i != ""]
            self._ng[keys[i]] = {j for j in data if (j[0] != "-") and (j[0] != "#")}
            self._allow[keys[i]] = {j[1:] for j in data if j[0] == "-"}

    def match(self, text) -> bool:
        ng = self.all_ng_words
        allow = self.all_excluded_words
        return any(x in text for x in ng) and (not any(x in text for x in allow))
    
    def why(self, txt):
        for i in self.all_ng_words:
            if i in txt:
                return i

    @property
    def all_ng_words(self) -> set:
        return set().union(*self._ng.values())
    @property
    def all_excluded_words(self) -> set:
        return set().union(*self._allow.values())

    @property
    def ng_word_hiragana(self) -> set:
        return self._ng["hira"]
    @property
    def ng_word_katakana(self) -> set:
        return self._ng["kana"]
    @property
    def ng_word_romaji(self) -> set:
        return self._ng["romaji"]

    @property
    def excluded_word_hiragana(self) -> set:
        return self._allow["hira"]
    @property
    def excluded_word_katakana(self) -> set:
        return self._allow["kana"]
    @property
    def excluded_word_romaji(self) -> set:
        return self._allow["romaji"]

def set_default_name(name):
    NGWords.set_default_name(name)

if __name__ == "__main__":
    print(NGWords(r"ngWords.txt").why("土日祝は割と1日1食とかしてる"))
    print(NGWords(r"ngWords_Hiraassssssss.txt").all_ng_words)  # FileNotFound