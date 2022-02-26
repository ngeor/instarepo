import datetime
import os.path
import re

import instarepo.fixers.context
import instarepo.git
import instarepo.github
from instarepo.fixers.base import MissingFileFix


def _repl(match: re.Match, year: int) -> str:
    is_year_range = match.group(4)
    if is_year_range:
        is_same_year = str(year) == match.group(4)
        if is_same_year:
            return match.group(0)
        else:
            return match.group(1) + match.group(2) + "-" + str(year)
    else:
        is_same_year = str(year) == match.group(2)
        if is_same_year:
            return match.group(0)
        else:
            return match.group(0) + "-" + str(year)


def update_copyright_year(contents: str, year: int) -> str:
    copyright_regex = re.compile(r"^(Copyright \(c\) )([0-9]{4})(-([0-9]{4}))?", re.M)
    return copyright_regex.sub(lambda m: _repl(m, year), contents)


class CopyrightYearFix:
    """
    Ensures the year in the license file copyright is up to date.

    Does not run for forks, private repos, and local git repos.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        self.context = context

    def run(self):
        if not self.context.repo or self.context.repo.private or self.context.repo.fork:
            return []
        filename = self.context.git.join("LICENSE")
        if not os.path.isfile(filename):
            return []
        with open(filename, "r", encoding="utf-8") as file:
            old_contents = file.read()
        new_contents = update_copyright_year(old_contents, datetime.date.today().year)
        if old_contents == new_contents:
            return []
        with open(filename, "w", encoding="utf8") as file:
            file.write(new_contents)
        self.context.git.add("LICENSE")
        msg = "chore: Updated copyright year in LICENSE"
        self.context.git.commit(msg)
        return [msg]


MIT_LICENSE = """MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


class MustHaveLicenseFix(MissingFileFix):
    """
    Ensures that a license file exists.

    Does not run for forks, private repos, and local git repos.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, "LICENSE")
        self.repo = context.repo

    def should_process_repo(self):
        return self.repo and not self.repo.private and not self.repo.fork

    def get_contents(self):
        contents = MIT_LICENSE.replace(
            "[year]", str(datetime.date.today().year)
        ).replace("[fullname]", self.git.user_name())
        return contents
