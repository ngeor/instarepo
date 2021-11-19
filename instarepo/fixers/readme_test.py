"""Unit tests for readme.py"""

import re
import instarepo.fixers.readme


def test_match_screenshot():
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

    def replacer(match: re.Match[str]) -> str:
        return (
            match.string[match.start() : match.start("filename")]
            + "/scrnshot.png"
            + match.string[match.end("filename") : match.end()]
        )

    actual = instarepo.fixers.readme.RE_MARKDOWN_IMAGE.sub(replacer, input_readme)
    assert actual == expected
