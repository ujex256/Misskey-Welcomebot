import ngwords

ng = {"r-18", "荒らす", "twitter", "ワード"}
allow = {"除外ワード", "除外ワード2", "スペースあり", "複数スペース"}


def test_ngwords():
    words = ngwords.NGWords("tests/test_ngwords.txt")
    assert words.all_ng_words == ng
    assert words.all_excluded_words == allow
    for word in ng:
        assert words.match(word)
    for word in allow:
        assert not words.match(word)
    assert words.why("くぁwせdR-18rftgyふじこ") == "r-18"
