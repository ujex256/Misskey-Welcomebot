import pytest
import emojis


messages = ["response.jsonは{'triggers': [], 'others': []}の形にしてください。",
            "response.jsonのトリガーのキーはkeywordsとemojiにしてください。",
            "[Errno 2] No such file or directory: 'aaaaaaaa'",
            "Invalid type for path: <class 'list'>. Expected str, PathLike, or NoneType."
]


@pytest.mark.parametrize("input,msg",
                         (["aaaaaaaa", messages[2]],
                          [[], messages[3]],
                          [{"d": "a"}, messages[0]],
                          [{"triggers": [{}], "others": []}, messages[1]]))
def test_emojiset_error(input, msg):
    error_cls = FileNotFoundError if isinstance(input, str) else emojis.ConfigJsonError
    with pytest.raises(error_cls) as e:
        emojis.EmojiSet(input)
    print(msg)
    assert str(e.value) == msg
