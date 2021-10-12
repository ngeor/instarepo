import argparse
import logging
import tempfile
from typing import Iterable

import requests

import instarepo.git
import instarepo.github
import instarepo.repo_source
import instarepo.fix
import instarepo.fixers.maven
import instarepo.fixers.missing_files
import instarepo.fixers.readme_image
import instarepo.fixers.repo_description


def main():
    args = parse_args()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    if args.subparser_name == "fix":
        main = Main(args)
        main.run()
    else:
        raise ValueError(f"Sub-parser {args.subparser_name} is not implemented")


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
        "--repo-prefix",
        action="store",
        help="Only process repositories whose name starts with the given prefix",
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Verbose output"
    )
    parser.add_argument(
        "--forks",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Process forks",
    )

    subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-commands help")
    list_parser = subparsers.add_parser("list", help="Lists the available repositories")
    fix_parser = subparsers.add_parser(
        "fix",
        description="Runs automatic fixes on the repositories",
        help="Runs automatic fixes on the repositories",
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
        self.repo_prefix: str = args.repo_prefix
        self.verbose: bool = args.verbose
        self.forks: bool = args.forks

    def run(self):
        repos = instarepo.repo_source.get_repos(
            self.github, repo_prefix=self.repo_prefix, forks=self.forks
        )
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
                instarepo.fixers.maven.MavenFix(self.git, self.repo),
                instarepo.fixers.missing_files.MustHaveEditorConfigFix(
                    self.git, self.repo
                ),
                instarepo.fixers.missing_files.MustHaveLicenseFix(self.git, self.repo),
                instarepo.fixers.missing_files.MustHaveReadmeFix(self.git, self.repo),
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
        html_url = self.github.create_merge_request(
            self.repo.full_name,
            self.branch_name,
            self.repo.default_branch,
            "instarepo automatic PR",
            format_body(changes),
        )
        logging.info("Created PR for repo %s - %s", self.repo.name, html_url)


def format_body(changes: Iterable[str]) -> str:
    body = "The following fixes have been applied:\n"
    for change in changes:
        lines = non_empty_lines(change)
        first = True
        for line in lines:
            if first:
                body += "- "
                first = False
            else:
                body += "  "
            body += line + "\n"
    return body


def non_empty_lines(s: str) -> Iterable[str]:
    lines = s.split("\n")
    stripped_lines = (line.strip() for line in lines)
    return (line for line in stripped_lines if line)


if __name__ == "__main__":
    main()
