import random

from utils import load_from_json_path


class ConfigJsonError(Exception):
    pass


class EmojiSet:
    def __init__(self, data: str | dict) -> None:
        """
        レスポンスの絵文字を返すクラス

        Args:
            data (str | dict): response.jsonのパス
        """
        if isinstance(data, dict):
            loaded = data
        else:
            loaded = load_from_json_path(data)
        self._check_format(loaded)

        self.response_emojis = loaded["triggers"]
        self.others = loaded["others"]

    def _check_format(self, json: dict) -> None:
        if not isinstance(json, dict) or sorted(json.keys()) != ["others", "triggers"]:
            raise ConfigJsonError(
                "response.jsonは{'triggers': [], 'others': []}の形にしてください。"
            )

        if any([sorted(i.keys()) != ["emoji", "keywords"] for i in json["triggers"]]):
            raise ConfigJsonError(
                "response.jsonのトリガーのキーはkeywordsとemojiにしてください。"
            )

    def get_response_emoji(self, text: str) -> str:
        for i in self.response_emojis:
            if any(j in text for j in i["keywords"]):
                if isinstance(i["emoji"], list):
                    return random.choice(i["emoji"])
                else:
                    return i["emoji"]
        else:
            return random.choice(self.others)
