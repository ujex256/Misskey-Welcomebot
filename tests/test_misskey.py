import json
import sys

sys.path.append("./src")
from src import misskey_api as misskey  # NOQA


def test_can_renote():
    with open("tests/test_note.json") as f:
        j = json.load(f)
    for i in j:
        assert misskey.can_renote(i) == i["r"]
