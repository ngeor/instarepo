import os
import os.path

import instarepo.git
import instarepo.github


class MustHaveReadmeFix:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
    ):
        self.git = git
        self.repo = repo

    def run(self):
        filename = os.path.join(self.git.dir, "README.md")
        if os.path.isfile(filename):
            return []
        with open(filename, "w") as f:
            f.write(f"# {self.repo.name}" + os.linesep)
            f.write(os.linesep)
            if self.repo.description:
                f.write(self.repo.description + os.linesep)
        self.git.add("README.md")
        self.git.commit("Adding README.md to repository")
        return ["Adding README.md to repository"]
