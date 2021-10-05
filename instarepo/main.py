import argparse
import os.path
import tempfile

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
            print("Processing ", repo.name)
            processor = RepoProcessor(repo, self.auth)
            processor.process()

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

    def process(self):
        self.prepare()
        self.run_fixes()
        if self.has_changes():
            self.create_merge_request()

    def prepare(self):
        self.git.create_branch("instarepo_branch")

    def run_fixes(self):
        with open(os.path.join(self.git.dir, "test.txt"), "w") as f:
            f.write("hello, world")
        self.git.add("test.txt")
        self.git.commit("Adding a test.txt file")

    def has_changes(self):
        if self.dry_run:
            return False
        return True

    def create_merge_request(self):
        if self.dry_run:
            print("Would have created PR")
            return
        self.git.push()
        html_url = instarepo.github.create_merge_request(
            self.auth,
            self.repo.full_name,
            "instarepo_branch",
            self.repo.default_branch,
            "instarepo automatic PR",
            "The following fixes have been applied",
        )
        print("A PR has been created: ", html_url)


if __name__ == "__main__":
    main()
