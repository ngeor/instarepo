"""Unit tests for readme.py"""

import re
from .readme import locate_badges, merge_badges, RE_MARKDOWN_IMAGE


def test_match_screenshot():
    """Tests replacing a screenshot with the module's regex"""
    input_readme = """
    # GodFather
A Delphi app to rename files (legacy project)

![screenshot](/GodFather/scrnshot.png?raw=true "Screenshot")
    """
    expected = """
    # GodFather
A Delphi app to rename files (legacy project)

![screenshot](/scrnshot.png?raw=true "Screenshot")
    """

    def replacer(match: re.Match) -> str:
        """The replacer function for the regex replacement"""
        return (
            match.string[match.start() : match.start("filename")]
            + "/scrnshot.png"
            + match.string[match.end("filename") : match.end()]
        )

    actual = RE_MARKDOWN_IMAGE.sub(replacer, input_readme)
    assert actual == expected


def test_locate_badges_one_badge():
    """Tests locating badges with a single badge"""
    input_readme = """# archetype-quickstart-jdk8

[![Maven Central](https://maven-badges.herokuapp.com/maven-central/com.github.ngeor/archetype-quickstart-jdk8/badge.svg)](https://maven-badges.herokuapp.com/maven-central/com.github.ngeor/archetype-quickstart-jdk8)

A Maven archetype for a simple Java app, updated for Java 8.

This is effectively the same as the maven-archetype-quickstart,
"""

    expected = (
        """# archetype-quickstart-jdk8
""",
        [
            "[![Maven Central](https://maven-badges.herokuapp.com/maven-central/com.github.ngeor/archetype-quickstart-jdk8/badge.svg)](https://maven-badges.herokuapp.com/maven-central/com.github.ngeor/archetype-quickstart-jdk8)"
        ],
        """A Maven archetype for a simple Java app, updated for Java 8.

This is effectively the same as the maven-archetype-quickstart,
""",
    )
    actual = locate_badges(input_readme)
    assert expected == actual


def test_locate_badges_no_badges():
    """Tests locating badges when no badges exist"""
    input_readme = """# some project

Some project description that goes on for a while
and even wraps multiple lines.

Some other text second paragraph here.
"""
    expected = (
        """# some project
""",
        [],
        """Some project description that goes on for a while
and even wraps multiple lines.

Some other text second paragraph here.
""",
    )
    actual = locate_badges(input_readme)
    assert expected == actual


def test_locate_and_merge_badges_one_badge():
    """Tests locating badges with a single badge and merging it back"""
    input_readme = """# archetype-quickstart-jdk8

[![Maven Central](https://maven-badges.herokuapp.com/maven-central/com.github.ngeor/archetype-quickstart-jdk8/badge.svg)](https://maven-badges.herokuapp.com/maven-central/com.github.ngeor/archetype-quickstart-jdk8)

A Maven archetype for a simple Java app, updated for Java 8.

This is effectively the same as the maven-archetype-quickstart,
"""
    before, badges, after = locate_badges(input_readme)
    merged = merge_badges(before, badges, after)
    assert input_readme == merged


def test_locate_and_merge_badges_no_badges():
    """Tests locating and merging badges when no badges exist"""
    input_readme = """# some project

Some project description that goes on for a while
and even wraps multiple lines.

Some other text second paragraph here.
"""
    before, badges, after = locate_badges(input_readme)
    merged = merge_badges(before, badges, after)
    assert input_readme == merged
