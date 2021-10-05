import argparse
import os.path
import tempfile
from typing import Iterable

import requests

import instarepo.git
import instarepo.github
import instarepo.repo_source


def main():
    args = parse_args()
    main = Main(args)
    main.run()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Apply changes on multiple repositories"
    )
    parser.add_argument(
        "-u", "--user", action="store", required=True, help="The GitHub username"
    )
    parser.add_argument(
        "-t", "--token", action="store", required=True, help="The GitHub token"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Do not actually push and create MR",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        default=False,
        help="Do not process all repositories, just one",
    )
    return parser.parse_args()


class Main:
    def __init__(self, args):
        self.auth = requests.auth.HTTPBasicAuth(args.user, args.token)
        self.dry_run: bool = args.dry_run
        self.sample: bool = args.sample

    def run(self):
        repos = instarepo.repo_source.get_repos(self.auth, self.sample)
        for repo in repos:
            self.process(repo)

    def process(self, repo: instarepo.github.Repo):
        print("Processing ", repo.name)
        with tempfile.TemporaryDirectory() as tmpdirname:
            print("Cloning repo into temp dir", tmpdirname)
            git = instarepo.git.clone(repo.ssh_url, tmpdirname)
            processor = RepoProcessor(repo, self.auth, git, self.dry_run)
            processor.process()


class RepoProcessor:
    def __init__(
        self,
        repo: instarepo.github.Repo,
        auth,
        git: instarepo.git.GitWorkingDir,
        dry_run: bool = False,
    ):
        self.repo = repo
        self.auth = auth
        self.git = git
        self.dry_run = dry_run
        self.branch_name = "instarepo_branch"

    def process(self):
        self.prepare()
        changes = self.run_fixes()
        if self.has_changes():
            if not changes:
                print("WARNING: Git reports changes but the internal changes have not.")
                print("This is likely a bug in the internal checker code.")
            self.create_merge_request(changes)
        else:
            if changes:
                print(
                    "WARNING: Git does not report changes but the internal checkers have reported the following changes:"
                )
                for change in changes:
                    print(change)
                print("This is likely a bug in the internal checker code.")
            else:
                print("No changes were made")

    def prepare(self):
        self.git.create_branch(self.branch_name)

    def run_fixes(self):
        with open(os.path.join(self.git.dir, "test.txt"), "w") as f:
            f.write("hello, world")
        self.git.add("test.txt")
        self.git.commit("Adding a test.txt file")
        return ["Adding a test.txt file"]

    def has_changes(self):
        current_sha = self.git.rev_parse(self.branch_name)
        main_sha = self.git.rev_parse(self.repo.default_branch)
        return current_sha != main_sha

    def create_merge_request(self, changes: Iterable[str]):
        body = "The following fixes have been applied:\n" + "\n".join(
            ["- " + x for x in changes]
        )
        if self.dry_run:
            print("Would have created PR")
            print(body)
            return
        self.git.push()
        html_url = instarepo.github.create_merge_request(
            self.auth,
            self.repo.full_name,
            self.branch_name,
            self.repo.default_branch,
            "instarepo automatic PR",
            body,
        )
        print("A PR has been created: ", html_url)


if __name__ == "__main__":
    main()
