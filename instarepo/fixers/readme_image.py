import os.path
import re

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

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, "README.md", "Fixed broken images in README")

    def convert(self, contents: str) -> str:
        return RE_MARKDOWN_IMAGE.sub(self.image_convert, contents)

    def image_convert(self, m: re.Match[str]) -> str:
        filename = m.group("filename")
        new_filename = self.find_new_filename(filename)
        return (
            m.string[m.start() : m.start("filename")]
            + new_filename
            + m.string[m.end("filename") : m.end()]
        )

    def find_new_filename(self, filename: str) -> str:
        abs_git_dir = os.path.abspath(self.git.dir)
        parts = [x for x in filename.replace("\\", "/").split("/") if x]
        while parts:
            x = abs_git_dir
            for p in parts:
                x = os.path.join(x, p)
            if os.path.isfile(x):
                return "/" + "/".join(parts)
            else:
                parts = parts[1:]
        return filename
