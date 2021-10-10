import datetime
import os.path

import instarepo.git
import instarepo.github


class MissingFileFix:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
        filename: str,
    ):
        self.git = git
        self.repo = repo
        self.filename = filename

    def run(self):
        full_filename = os.path.join(self.git.dir, self.filename)
        if os.path.isfile(full_filename):
            return []
        if not self.should_process_repo():
            return []
        contents = self.get_contents()
        with open(full_filename, "w", encoding="utf8") as f:
            f.write(contents)
        self.git.add(self.filename)
        msg = "Adding " + self.filename
        self.git.commit(msg)
        return [msg]

    def get_contents(self) -> str:
        return None

    def should_process_repo(self) -> bool:
        return True


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
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
    ):
        super().__init__(git, repo, "LICENSE")

    def should_process_repo(self):
        return not self.repo.private and not self.repo.fork

    def get_contents(self):
        contents = MIT_LICENSE.replace(
            "[year]", str(datetime.date.today().year)
        ).replace("[fullname]", self.git.user_name())
        return contents


class MustHaveReadmeFix(MissingFileFix):
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
    ):
        super().__init__(git, repo, "README.md")

    def get_contents(self):
        contents = f"# {self.repo.name}\n"
        if self.repo.description:
            contents = contents + "\n" + self.repo.description + "\n"
        return contents


EDITOR_CONFIG = """# Editor configuration, see https://editorconfig.org
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 4
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 120

[*.sh]
end_of_line = lf
"""


class MustHaveEditorConfigFix(MissingFileFix):
    def __init__(self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo):
        super().__init__(git, repo, ".editorconfig")

    def get_contents(self):
        return EDITOR_CONFIG
