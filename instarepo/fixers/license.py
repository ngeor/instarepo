import datetime
import os.path
import re

from typing import Optional

import instarepo.git
import instarepo.github
from instarepo.fixers.base import MissingFileFix


def _repl(m: re.Match, year: int) -> str:
    is_year_range = m.group(4)
    if is_year_range:
        is_same_year = str(year) == m.group(4)
        if is_same_year:
            return m.group(0)
        else:
            return m.group(1) + m.group(2) + "-" + str(year)
    else:
        is_same_year = str(year) == m.group(2)
        if is_same_year:
            return m.group(0)
        else:
            return m.group(0) + "-" + str(year)


def update_copyright_year(contents: str, year: int) -> str:
    x = re.compile(r"^(Copyright \(c\) )([0-9]{4})(-([0-9]{4}))?", re.M)
    return x.sub(lambda m: _repl(m, year), contents)


class CopyrightYearFix:
    """
    Ensures the year in the license file copyright is up to date.

    Does not run for forks, private repos, and local git repos.
    """

    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: Optional[instarepo.github.Repo],
        **kwargs
    ):
        self.git = git
        self.repo = repo

    def run(self):
        if not self.repo or self.repo.private or self.repo.fork:
            return []
        filename = os.path.join(self.git.dir, "LICENSE")
        if not os.path.isfile(filename):
            return []
        with open(filename, "r", encoding="utf-8") as f:
            old_contents = f.read()
        new_contents = update_copyright_year(old_contents, datetime.date.today().year)
        if old_contents == new_contents:
            return []
        with open(filename, "w", encoding="utf8") as f:
            f.write(new_contents)
        self.git.add("LICENSE")
        msg = "chore: Updated copyright year in LICENSE"
        self.git.commit(msg)
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

    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: Optional[instarepo.github.Repo],
        **kwargs
    ):
        super().__init__(git, "LICENSE")
        self.repo = repo

    def should_process_repo(self):
        return self.repo and not self.repo.private and not self.repo.fork

    def get_contents(self):
        contents = MIT_LICENSE.replace(
            "[year]", str(datetime.date.today().year)
        ).replace("[fullname]", self.git.user_name())
        return contents
