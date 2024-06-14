import json

import misskey_api as misskey  # NOQA


def test_can_renote():
    with open("tests/test_note_renote.json") as f:
        j = json.load(f)
    for i in j:
        assert misskey.can_renote(i) == i["r"]


def test_can_reply():
    misskey.USERNAME = "youkoso_bot"
    with open("tests/test_note_reply.json") as f:
        j = json.load(f)
    for i in j:
        assert misskey.can_reply(i) == i["r"]
