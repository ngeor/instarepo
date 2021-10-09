import argparse
import logging
import tempfile
from typing import Iterable

import requests

import instarepo.git
import instarepo.github
import instarepo.repo_source
import instarepo.fix
import instarepo.fixers.must_have_license
import instarepo.fixers.must_have_readme
import instarepo.fixers.readme_image
import instarepo.fixers.repo_description


def main():
    args = parse_args()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
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
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Verbose output"
    )
    return parser.parse_args()


class Main:
    def __init__(self, args):
        if args.dry_run:
            self.github = instarepo.github.GitHub(
                auth=requests.auth.HTTPBasicAuth(args.user, args.token),
            )
        else:
            self.github = instarepo.github.ReadWriteGitHub(
                auth=requests.auth.HTTPBasicAuth(args.user, args.token),
            )
        self.dry_run: bool = args.dry_run
        self.sample: bool = args.sample
        self.verbose: bool = args.verbose

    def run(self):
        repos = instarepo.repo_source.get_repos(self.github, self.sample)
        for repo in repos:
            self.process(repo)

    def process(self, repo: instarepo.github.Repo):
        logging.info("Processing repo %s", repo.name)
        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug("Cloning repo into temp dir %s", tmpdirname)
            git = instarepo.git.clone(repo.ssh_url, tmpdirname, quiet=not self.verbose)
            processor = RepoProcessor(repo, self.github, git, self.dry_run)
            processor.process()


class RepoProcessor:
    def __init__(
        self,
        repo: instarepo.github.Repo,
        github: instarepo.github.GitHub,
        git: instarepo.git.GitWorkingDir,
        dry_run: bool = False,
    ):
        self.repo = repo
        self.github = github
        self.git = git
        self.dry_run = dry_run
        self.branch_name = "instarepo_branch"

    def process(self):
        self.prepare()
        changes = self.run_fixes()
        if self.has_changes():
            if not changes:
                logging.warning("Git reports changes but the internal changes do not.")
                logging.warning("This is likely a bug in the internal checker code.")
            self.create_merge_request(changes)
        else:
            if changes:
                logging.warning(
                    "Git does not report changes but the internal checkers report the following changes:"
                )
                for change in changes:
                    logging.warning(change)
                logging.warning("This is likely a bug in the internal checker code.")
            else:
                logging.debug("No changes found for repo %s", self.repo.name)

    def prepare(self):
        self.git.create_branch(self.branch_name)

    def run_fixes(self):
        fix = instarepo.fix.CompositeFix(
            [
                instarepo.fixers.must_have_license.MustHaveLicenseFix(
                    self.git, self.repo
                ),
                instarepo.fixers.must_have_readme.MustHaveReadmeFix(
                    self.git, self.repo
                ),
                instarepo.fixers.readme_image.ReadmeFix(self.git),
                instarepo.fixers.repo_description.RepoDescriptionFix(
                    self.github, self.git, self.repo
                ),
            ]
        )
        return fix.run()

    def has_changes(self):
        current_sha = self.git.rev_parse(self.branch_name)
        main_sha = self.git.rev_parse(self.repo.default_branch)
        return current_sha != main_sha

    def create_merge_request(self, changes: Iterable[str]):
        if self.dry_run:
            logging.info("Would have created PR for repo %s", self.repo.name)
            return
        self.git.push()
        body = "The following fixes have been applied:\n" + "\n".join(
            ["- " + x for x in changes]
        )
        html_url = self.github.create_merge_request(
            self.repo.full_name,
            self.branch_name,
            self.repo.default_branch,
            "instarepo automatic PR",
            body,
        )
        logging.info("Created PR for repo %s - %s", self.repo.name, html_url)


if __name__ == "__main__":
    main()
