import datetime
import os
import os.path

import requests

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
        if not filename:
            raise ValueError("filename cannot be empty")
        parts = filename.replace("\\", "/").split("/")
        for part in parts:
            if not part:
                raise ValueError(f"Found empty path segment in {filename}")
        self.directory_parts = parts[0:-1]
        self.filename_part = parts[-1]

    def run(self):
        self.ensure_directories()
        relative_filename = os.path.join(*self.directory_parts, self.filename_part)
        full_filename = os.path.join(self.git.dir, relative_filename)
        if os.path.isfile(full_filename):
            return []
        if not self.should_process_repo():
            return []
        contents = self.get_contents()
        with open(full_filename, "w", encoding="utf8") as f:
            f.write(contents)
        self.git.add(relative_filename)
        msg = "Adding " + relative_filename
        self.git.commit(msg)
        return [msg]

    def get_contents(self) -> str:
        return None

    def should_process_repo(self) -> bool:
        return True

    def ensure_directories(self):
        root = self.git.dir
        for dir in self.directory_parts:
            root = os.path.join(root, dir)
            if not os.path.isdir(root):
                os.mkdir(root)


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


FUNDING_YML = """# These are supported funding model platforms

github: # Replace with up to 4 GitHub Sponsors-enabled usernames e.g., [user1, user2]
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective username
ko_fi: # Replace with a single Ko-fi username
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
custom: ['https://ngeor.com/support/']
"""


class MustHaveGitHubFundingFix(MissingFileFix):
    def __init__(self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo):
        super().__init__(git, repo, ".github/FUNDING.yml")

    def get_contents(self):
        return FUNDING_YML


MAVEN_YML = """# This workflow will build a Java project with Maven, and cache/restore any dependencies to improve the workflow execution time
# For more information see: https://help.github.com/actions/language-and-framework-guides/building-and-testing-java-with-maven

name: Java CI with Maven

on:
  push:
    branches: [ trunk ]
  pull_request:
    branches: [ trunk ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up JDK 11
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'adopt'
        cache: maven
    - name: Build with Maven
      run: mvn -B package --file pom.xml
"""


class MustHaveMavenGitHubWorkflow(MissingFileFix):
    def __init__(self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo):
        super().__init__(git, repo, ".github/workflows/maven.yml")

    def get_contents(self):
        return MAVEN_YML

    def should_process_repo(self):
        return os.path.isfile(os.path.join(self.git.dir, "pom.xml"))


class MustHaveMavenGitIgnore(MissingFileFix):
    def __init__(self, git: instarepo.git.GitWorkingDir, repo: instarepo.github.Repo):
        super().__init__(git, repo, ".gitignore")

    def should_process_repo(self):
        return os.path.isfile(os.path.join(self.git.dir, "pom.xml"))

    def get_contents(self):
        # https://github.com/github/gitignore/blob/master/Maven.gitignore
        response = requests.get(
            "https://raw.githubusercontent.com/github/gitignore/master/Maven.gitignore"
        )
        response.raise_for_status()
        return response.text
