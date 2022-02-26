import datetime
import os.path
import subprocess


class GitWorkingDir:
    def __init__(self, directory: str, quiet: bool = False):
        self.dir = directory
        self.quiet = quiet

    def join(self, *args) -> str:
        root = self.dir
        for arg in args:
            parts = arg.replace("\\", "/").split("/")
            for part in parts:
                root = os.path.join(root, part)
        return root

    def isfile(self, *args) -> bool:
        return os.path.isfile(self.join(*args))

    def isdir(self, *args) -> bool:
        return os.path.isdir(self.join(*args))

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

    # pylint: disable=invalid-name
    def rm(self, file: str) -> None:
        subprocess.run(["git", "rm", file], check=True, cwd=self.dir)

    def commit(self, message: str) -> None:
        args = ["git", "commit"]
        if self.quiet:
            args.append("-q")
        args.extend(["-m", message])
        subprocess.run(args, check=True, cwd=self.dir)

    def push(self, force: bool = False, remote_name: str = "origin") -> None:
        args = ["git", "push"]
        if self.quiet:
            args.append("-q")
        if force:
            args.append("--force-with-lease")
        args.extend(["-u", remote_name, "HEAD"])
        subprocess.run(
            args,
            check=True,
            cwd=self.dir,
        )

    def delete_local_branch(self, branch_name: str) -> None:
        args = ["git", "branch"]
        if self.quiet:
            args.append("-q")
        args.extend(["-D", branch_name])
        subprocess.run(
            args,
            check=True,
            cwd=self.dir,
        )

    def delete_remote_branch(
        self, branch_name: str, remote_name: str = "origin"
    ) -> None:
        args = ["git", "push"]
        if self.quiet:
            args.append("-q")
        args.extend(["--delete", remote_name, branch_name])
        subprocess.run(
            args,
            check=True,
            cwd=self.dir,
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

    def is_remote_branch_present(self, branch: str, remote="origin"):
        remote_branch_sha = ""
        try:
            remote_branch_sha = self.rev_parse(f"remotes/{remote}/{branch}")
        except:  # pylint: disable=bare-except
            pass
        return len(remote_branch_sha) > 0

    def get_behind_ahead(self, base: str, head: str):
        # git rev-list --left-right --count origin/trunk...trunk
        # 12      0
        result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", f"{base}...{head}"],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        parts = result.stdout.split("\t")
        return int(parts[0]), int(parts[1])

    def get_remote_url(self):
        # git remote get-url origin
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        return result.stdout.strip()

    def get_default_branch(self):
        # git symbolic-ref refs/remotes/origin/HEAD -> refs/remotes/origin/trunk
        prefix = "refs/remotes/origin/"
        ref = prefix + "HEAD"
        result = subprocess.run(
            ["git", "symbolic-ref", ref],
            check=True,
            cwd=self.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        output = result.stdout.strip()
        return output[len(prefix) :]


def clone(ssh_url: str, clone_dir: str, quiet: bool = False) -> GitWorkingDir:
    args = ["git", "clone"]
    if quiet:
        args.append("-q")
    args.extend([ssh_url, clone_dir])
    subprocess.run(args, check=True)
    return GitWorkingDir(clone_dir, quiet)
