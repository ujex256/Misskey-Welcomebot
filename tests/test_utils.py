import json

import utils


def test_can_renote():
    with open("tests/test_note_renote.json") as f:
        j = json.load(f)
    for i in j:
        assert utils.can_renote(i) == i["r"]


def test_can_reply():
    username = "youkoso_bot"
    with open("tests/test_note_reply.json") as f:
        j = json.load(f)
    for i in j:
        assert utils.can_reply(i, username) == i["r"]
