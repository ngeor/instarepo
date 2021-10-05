import subprocess


class GitWorkingDir:
    def __init__(self, dir: str):
        self.dir = dir

    def create_branch(self, name: str) -> None:
        subprocess.run(
            ["git", "checkout", "-b", name],
            check=True,
            cwd=self.dir,
        )

    def add(self, file: str) -> None:
        subprocess.run(["git", "add", file], check=True, cwd=self.dir)

    def commit(self, message: str) -> None:
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=self.dir)

    def push(self) -> None:
        subprocess.run(
            ["git", "push", "-u", "origin", "HEAD"], check=True, cwd=self.dir
        )

    def rev_parse(self, branch_name: str) -> str:
        """
        Gets the SHA of the given branch.
        """
        result = subprocess.run(
            ["git", "rev-parse", branch_name],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        return result.stdout.strip()


def clone(ssh_url: str, clone_dir: str) -> GitWorkingDir:
    subprocess.run(["git", "clone", ssh_url, clone_dir], check=True)
    return GitWorkingDir(clone_dir)
