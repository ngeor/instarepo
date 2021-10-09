import datetime
import os.path

import instarepo.git
import instarepo.github


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


class MustHaveLicenseFix:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
    ):
        self.git = git
        self.repo = repo

    def run(self):
        filename = os.path.join(self.git.dir, "LICENSE")
        if os.path.isfile(filename):
            return []
        if self.repo.private or self.repo.fork:
            return []
        contents = MIT_LICENSE.replace(
            "[year]", str(datetime.date.today().year)
        ).replace("[fullname]", self.git.user_name())
        with open(filename, "w", encoding="utf8") as f:
            f.write(contents)
        self.git.add("LICENSE")
        self.git.commit("Adding LICENSE to repository")
        return ["Adding LICENSE to repository"]
