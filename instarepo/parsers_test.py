from .parsers import any_char, one_char_if, many, word, combine_and


def test_any_char():
    x, y = any_char()("abc")
    assert x == "a"
    assert y == "bc"


def test_one_char_if():
    x, y = one_char_if(lambda p: p >= "a")("abc")
    assert x == "a"
    assert y == "bc"
    x, y = one_char_if(lambda p: p < "a")("abc")
    assert x == ""
    assert y == "abc"


def test_many():
    lower_case_parser = one_char_if(lambda x: x >= "a" and x <= "z")
    x, y = many(lower_case_parser)("hello world")
    assert x == "hello"
    assert y == " world"


def test_word():
    x, y = word()("Hello, world!")
    assert x == "Hello"
    assert y == ", world!"


def test_combine_and():
    first = word()
    second = one_char_if(lambda x: x == ",")
    x, y = combine_and(first, second)("Hello, world!")
    assert x == "Hello,"
    assert y == " world!"
