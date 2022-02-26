"""
Fixers for the README.md file
"""

import os.path
import re
from typing import List, Tuple

import instarepo.fixers.context
import instarepo.git
from .base import SingleFileFix

# \w matches [a-zA-Z0-9_]
RE_MARKDOWN_IMAGE = re.compile(
    r'!\[[^]]*\]\((?P<filename>/[\w/\.]+)\?raw=true "[^"]*"\)'
)


class ReadmeImageFix(SingleFileFix):
    """
    Finds broken images in the `README.md` file.
    Able to correct images that were moved one or more
    folders up but the user forgot to update them in the `README.md` file.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        """Creates an instance of this class"""
        super().__init__(context.git, "README.md", "fix: Fixed broken images in README")

    def convert(self, contents: str) -> str:
        return RE_MARKDOWN_IMAGE.sub(self.image_convert, contents)

    def image_convert(self, match: re.Match) -> str:
        filename = match.group("filename")
        new_filename = self.find_new_filename(filename)
        return (
            match.string[match.start() : match.start("filename")]
            + new_filename
            + match.string[match.end("filename") : match.end()]
        )

    def find_new_filename(self, filename: str) -> str:
        """
        Finds a new filename for the broken image.
        Removes leading parts of the given path until a matching
        filename is found.
        """
        abs_git_dir = os.path.abspath(self.git.dir)
        parts = [x for x in filename.replace("\\", "/").split("/") if x]
        while parts:
            possible_path = os.path.join(abs_git_dir, *parts)
            if os.path.isfile(possible_path):
                return "/" + "/".join(parts)
            parts = parts[1:]
        return filename


def locate_badges(readme_contents: str) -> Tuple[str, List[str], str]:
    before_badges = []
    badges = []
    after_badges = []
    state = 0
    for line in readme_contents.splitlines():
        if state == 0:
            if _is_badge_line(line):
                state = 1
                badges.append(line)
            else:
                before_badges.append(line)
        elif state == 1:
            if _is_badge_line(line):
                badges.append(line)
            else:
                state = 2
                after_badges.append(line)
        else:
            after_badges.append(line)
    if state == 0:
        # no badges were found, try to split based on headline
        return (_join_lines(before_badges[0:1]), [], _join_lines(before_badges[1:]))
    return (_join_lines(before_badges), badges, _join_lines(after_badges))


def _is_badge_line(line: str) -> bool:
    return line.startswith("[![")


def _join_lines(lines: List[str]) -> str:
    return "\n".join(_strip_empty_lines(lines)) + "\n"


def _strip_empty_lines(lines: List[str]) -> List[str]:
    return _strip_trailing_empty_lines(_strip_leading_empty_lines(lines))


def _strip_leading_empty_lines(lines: List[str]) -> List[str]:
    i = 0
    while i < len(lines) and len(lines[i]) == 0:
        i += 1
    return lines[i:]


def _strip_trailing_empty_lines(lines: List[str]) -> List[str]:
    i = len(lines) - 1
    while i >= 0 and len(lines[i]) == 0:
        i -= 1
    return lines[0 : i + 1]


def merge_badges(before_text: str, badges: List[str], after_text: str) -> str:
    if badges:
        return before_text + "\n" + "\n".join(badges) + "\n\n" + after_text
    return before_text + "\n" + after_text
