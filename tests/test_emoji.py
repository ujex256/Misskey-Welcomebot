import pytest

import emojis

inputs = [
    ["aaa", "[Errno 2] No such file or directory: 'aaa'", FileNotFoundError],
    [
        [],
        "Invalid type for path: <class 'list'>. Expected str, PathLike, or NoneType.",
        TypeError,
    ],
    [
        {"a": "b"},
        "response.jsonは{'triggers': [], 'others': []}の形にしてください。",
        emojis.ConfigJsonError,
    ],
    [
        {"triggers": [{}], "others": []},
        "response.jsonのトリガーのキーはkeywordsとemojiにしてください。",
        emojis.ConfigJsonError,
    ],
]


@pytest.mark.parametrize("input, msg, exception", inputs)
def test_emojiset_error(input, msg, exception):
    with pytest.raises(exception) as e:
        emojis.EmojiSet(input)
    print(msg)
    assert str(e.value) == msg
