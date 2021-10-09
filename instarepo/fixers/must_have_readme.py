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
        with open(filename, "w", encoding="utf8") as f:
            f.write(f"# {self.repo.name}\n")
            if self.repo.description:
                f.write("\n" + self.repo.description + "\n")
        self.git.add("README.md")
        self.git.commit("Adding README.md to repository")
        return ["Adding README.md to repository"]
