import json
import random
from io import StringIO
from typing import Any


class ConfigJsonError(Exception):
    pass


class EmojiSet:
    def __init__(self, data: str | StringIO) -> None:
        if isinstance(data, str):
            with open(f"{data}.json", "r") as f:
                loaded = json.load(f)
        else:
            loaded = data.read()
        self._check_format(loaded)

        self.response_emojis = loaded["triggers"]
        self.others = loaded["others"]

    def _check_format(json: Any) -> None:
        if not isinstance(json, dict) or tuple(json.keys()) != ("triggers", "others"):
            raise ConfigJsonError("response.jsonは{'triggers': [], 'others': []}の形にしてください。")

        if any([tuple(i.keys()) != ("keywords", "emoji") for i in json["triggers"]]):
            raise ConfigJsonError("response.jsonのトリガーのキーはkeywordsとemojiにしてください。")

    def get_response_emoji(self, text: str) -> str:
        for i in self.response_emojis:
            if any(j in text for j in i["keywords"]):
                if isinstance(i["emoji"], list):
                    return random.choice(i["emoji"])
                else:
                    return i["emoji"]
        else:
            return random.choice(self.others)
