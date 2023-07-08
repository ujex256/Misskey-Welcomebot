import pytest

from src import emojis


messages = ["response.jsonは{'triggers': [], 'others': []}の形にしてください。",
            "response.jsonのトリガーのキーはkeywordsとemojiにしてください。",
            "[Errno 2] No such file or directory: 'aaaaaaaa'"]


@pytest.mark.parametrize("input,msg",
                         (["aaaaaaaa", messages[2]],
                          [[], messages[0]],
                          [{"d": "a"}, messages[0]],
                          [{"triggers": [{}], "others": []}, messages[1]]))
def test_emojiset_error(input, msg):
    error_cls = FileNotFoundError if isinstance(input, str) else emojis.ConfigJsonError
    with pytest.raises(error_cls) as e:
        emojis.EmojiSet(input)
    assert str(e.value) == msg
