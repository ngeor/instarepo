import re
import instarepo.fixers.readme_image


def f(m: re.Match[str]) -> str:
    return (
        m.string[m.start() : m.start("filename")]
        + "/scrnshot.png"
        + m.string[m.end("filename") : m.end()]
    )


def test_match_screenshot():
    s = """
    # GodFather
A Delphi app to rename files (legacy project)

![screenshot](/GodFather/scrnshot.png?raw=true "Screenshot")
    """
    expected = """
    # GodFather
A Delphi app to rename files (legacy project)

![screenshot](/scrnshot.png?raw=true "Screenshot")
    """
    x = instarepo.fixers.readme_image.RE_MARKDOWN_IMAGE.sub(f, s)
    assert x == expected