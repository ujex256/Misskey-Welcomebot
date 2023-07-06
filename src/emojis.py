import json
import random
from typing import Any


def _check_format(json: Any) -> None:
    if not isinstance(json, dict):
        raise Exception("response.jsonは{'triggers': [], 'other': []}の形にしてください。")
    if any([tuple(i.keys()) != ("keywords", "emoji") for i in json["triggers"]]):
        raise Exception("response.jsonのトリガーのキーはkeywordsとemojiにしてください。")


def get_response_emoji(text: str) -> str:
    for i in RESPONSE_EMOJIS:
        if any(j in text for j in i["keywords"]):
            if isinstance(i["emoji"], list):
                return random.choice(i["emoji"])
            else:
                return i["emoji"]
    else:
        return random.choice(OTHERS)


with open("response.json", "r") as f:
    loaded = json.load(f)

    RESPONSE_EMOJIS = loaded["triggers"]
    OTHERS = loaded["other"]
    _check_format(RESPONSE_EMOJIS)
