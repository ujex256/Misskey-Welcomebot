from src import ngwords


ng = {"r-18", "荒らす", "twitter", "ワード"}
allow = {"除外ワード", "除外ワード2"}


def test_ngwords():
    _ng = ngwords.NGWords("tests/test_ngwords.txt")
    assert _ng.all_ng_words == ng
    assert _ng.all_excluded_words == allow
    for word in ng:
        assert _ng.match(word)
    for word in allow:
        assert not _ng.match(word)
    assert _ng.why("くぁwせdR-18rftgyふじこ") == "r-18"
