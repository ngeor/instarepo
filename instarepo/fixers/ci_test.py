"""
Unit tests for ci.py
"""

from .ci import remove_travis_badge


def test_badge():
    """Tests removing the Travis badge"""
    x = "[![Build Status](https://travis-ci.org/ngeor/games.svg?branch=master)](https://travis-ci.org/ngeor/games)"
    assert remove_travis_badge(x) == ""

    x = "hi"
    assert remove_travis_badge(x) == x
