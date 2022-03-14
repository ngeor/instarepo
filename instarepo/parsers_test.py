from .parsers import any_char, one_char_if, many, word, combine_and


def test_any_char():
    parsed, remaining = any_char()("abc")
    assert parsed == "a"
    assert remaining == "bc"


def test_one_char_if():
    parsed, remaining = one_char_if(lambda p: p >= "a")("abc")
    assert parsed == "a"
    assert remaining == "bc"
    parsed, remaining = one_char_if(lambda p: p < "a")("abc")
    assert parsed == ""
    assert remaining == "abc"


def test_many():
    lower_case_parser = one_char_if(lambda x: x >= "a" and x <= "z")
    parsed, remaining = many(lower_case_parser)("hello world")
    assert parsed == "hello"
    assert remaining == " world"


def test_word():
    parsed, remaining = word()("Hello, world!")
    assert parsed == "Hello"
    assert remaining == ", world!"


def test_combine_and():
    first = word()
    second = one_char_if(lambda x: x == ",")
    parsed, remaining = combine_and(first, second)("Hello, world!")
    assert parsed == "Hello,"
    assert remaining == " world!"
