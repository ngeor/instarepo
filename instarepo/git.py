import datetime
import subprocess


class GitWorkingDir:
    def __init__(self, dir: str, quiet: bool = False):
        self.dir = dir
        self.quiet = quiet

    def create_branch(self, name: str) -> None:
        args = ["git", "checkout"]
        if self.quiet:
            args.append("-q")
        args.extend(["-b", name])
        subprocess.run(
            args,
            check=True,
            cwd=self.dir,
        )

    def checkout(self, name: str) -> None:
        args = ["git", "checkout"]
        if self.quiet:
            args.append("-q")
        args.append(name)
        subprocess.run(
            args,
            check=True,
            cwd=self.dir,
        )

    def add(self, file: str) -> None:
        subprocess.run(["git", "add", file], check=True, cwd=self.dir)

    def commit(self, message: str) -> None:
        args = ["git", "commit"]
        if self.quiet:
            args.append("-q")
        args.extend(["-m", message])
        subprocess.run(args, check=True, cwd=self.dir)

    def push(self) -> None:
        subprocess.run(
            ["git", "push", "-u", "origin", "HEAD"], check=True, cwd=self.dir
        )

    def rev_parse(self, branch_name: str) -> str:
        """
        Gets the SHA of the given branch.
        """
        result = subprocess.run(
            ["git", "rev-parse", "-q", "--verify", branch_name],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        return result.stdout.strip()

    def current_branch_name(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        return result.stdout.strip()

    def user_name(self) -> str:
        """
        Gets the `user.name` configured property.
        """
        result = subprocess.run(
            ["git", "config", "user.name"],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        return result.stdout.strip()

    def rev_list(self, since, until, reverse=False):
        args = ["git", "rev-list", f"--since={since}", f"--until={until}"]
        if reverse:
            args.append("--reverse")
        args.append("HEAD")
        result = subprocess.run(
            args, check=True, cwd=self.dir, encoding="utf-8", stdout=subprocess.PIPE
        )
        return result.stdout.splitlines()

    def commit_date(self, commit_id):
        result = subprocess.run(
            ["git", "show", "-s", "--format=%ci", commit_id],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )

        # the result looks like 2017-02-20 21:28:35 +0100
        return datetime.datetime.strptime(
            result.stdout.split(" ")[0], "%Y-%m-%d"
        ).date()


def clone(ssh_url: str, clone_dir: str, quiet: bool = False) -> GitWorkingDir:
    args = ["git", "clone"]
    if quiet:
        args.append("-q")
    args.extend([ssh_url, clone_dir])
    subprocess.run(args, check=True)
    return GitWorkingDir(clone_dir, quiet)
