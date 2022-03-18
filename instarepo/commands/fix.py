"""
Applies fixes to a repository that is either locally checked out
or remote on GitHub.
"""
import logging
import tempfile
from typing import Iterable

import instarepo.git
import instarepo.github
import instarepo.repo_source

from ..credentials import build_requests_auth
from ..fixers.discovery import (
    all_fixer_classes,
    select_fixer_classes,
)
from ..fixers.naming import fixer_class_to_fixer_key


class FixCommand:
    """
    Applies fixes to a repository that is either locally checked out
    or remote on GitHub.
    """

    def __init__(self, args):
        if args.local_dir:
            self.delegate = FixLocal(args)
        else:
            self.delegate = FixRemote(args)

    def run(self):
        self.delegate.run()


class FixBase:
    """
    Base class for common features among FixLocal and FixRemote.
    """

    def __init__(self, args):
        self.dry_run: bool = args.dry_run
        self.verbose: bool = args.verbose
        self.fixer_classes = select_fixer_classes(args.only_fixers, args.except_fixers)
        self.config = instarepo.fixers.config.load_config(args.config_file)

    def run(self):
        if not self.fixer_classes:
            logging.error("No fixers selected!")
            return
        logging.debug(
            "Using fixers %s",
            ", ".join(map(fixer_class_to_fixer_key, self.fixer_classes)),
        )


class FixLocal(FixBase):
    """
    Applies fixes to a locally checked-out repository.
    """

    def __init__(self, args):
        super().__init__(args)
        if not args.local_dir:
            raise ValueError("local_dir must be specified")
        self.local_dir = args.local_dir

    def run(self):
        super().run()
        logging.info("Processing local repo %s", self.local_dir)
        git = instarepo.git.GitWorkingDir(self.local_dir, quiet=not self.verbose)
        context = instarepo.fixers.context.Context(
            git=git, config=self.config, verbose=self.verbose
        )
        if context.get_setting("enabled"):
            composite_fixer = create_composite_fixer(self.fixer_classes, context)
            composite_fixer.run()


BRANCH_NAME = "instarepo_branch"


class FixRemote(FixBase):
    """
    Applies fixes to a GitHub repository.
    """

    def __init__(self, args):
        super().__init__(args)
        if args.local_dir:
            raise ValueError("local_dir must be empty")
        auth = build_requests_auth(args)
        if args.dry_run:
            self.github = instarepo.github.GitHub(auth=auth)
        else:
            self.github = instarepo.github.ReadWriteGitHub(auth=auth)
        self.auto_merge = args.auto_merge
        self.force = args.force
        self.repo_source = (
            instarepo.repo_source.RepoSourceBuilder()
            .with_github(self.github)
            .with_args(args)
            .build()
        )

    def run(self):
        super().run()
        repos = self.repo_source.get()
        for repo in repos:
            if self.config.get_setting(repo.full_name, "enabled"):
                self._process(repo)

    def _process(self, repo: instarepo.github.Repo):
        logging.info("Processing repo %s", repo.name)
        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug("Cloning repo into temp dir %s", tmpdirname)
            git = instarepo.git.clone(repo.ssh_url, tmpdirname, quiet=not self.verbose)
            self._process_in_temp_directory(repo, git)

    def _process_in_temp_directory(
        self, repo: instarepo.github.Repo, git: instarepo.git.GitWorkingDir
    ):
        is_remote_branch_present = git.is_remote_branch_present(BRANCH_NAME)
        needs_force_push = False
        behind = 0
        ahead = 0
        if is_remote_branch_present:
            behind, ahead = git.get_behind_ahead(
                f"origin/{repo.default_branch}", f"origin/{BRANCH_NAME}"
            )
            logging.debug(
                "Remote branch exists and is %d commits behind and %d commits ahead of %s",
                behind,
                ahead,
                repo.default_branch,
            )
            if self._should_start_from_scratch(behind, ahead, git):
                git.create_branch(BRANCH_NAME)
                needs_force_push = True
                behind = 0
                ahead = 0
            else:
                git.checkout(BRANCH_NAME)
        else:
            git.create_branch(BRANCH_NAME)
        context = instarepo.fixers.context.Context(
            git=git,
            config=self.config,
            repo=repo,
            github=self.github,
            verbose=self.verbose,
        )
        composite_fixer = create_composite_fixer(
            self.fixer_classes,
            context,
        )
        changes = composite_fixer.run()
        if changes:
            self._create_merge_request(repo, git, changes, needs_force_push)
        elif ahead > 0 and self.auto_merge:
            # no changes in this run, but we are ahead of default branch, we can auto-merge
            merged = self._auto_merge_existing_mr(repo)
            if is_remote_branch_present and merged:
                if self.dry_run:
                    logging.info("Would have deleted remote branch")
                else:
                    git.delete_remote_branch(BRANCH_NAME)
        elif ahead == 0:
            # no changes and at the same point as the default branch, we can auto-close the MR
            if is_remote_branch_present:
                if self.dry_run:
                    logging.info("Would have deleted remote branch")
                else:
                    git.delete_remote_branch(BRANCH_NAME)
            self._close_mr_if_exists(repo)

    def _create_merge_request(
        self,
        repo: instarepo.github.Repo,
        git: instarepo.git.GitWorkingDir,
        changes: Iterable[str],
        needs_force_push: bool,
    ):
        if self.dry_run:
            logging.info("Would have created PR for repo %s", repo.name)
            return
        git.push(force=needs_force_push)
        if len(self._list_merge_requests(repo)) > 0:
            logging.info("PR already exists for repo %s", repo.name)
        else:
            html_url = self.github.create_merge_request(
                repo.full_name,
                BRANCH_NAME,
                repo.default_branch,
                "instarepo automatic PR",
                format_body(changes),
            )
            logging.info("Created PR for repo %s - %s", repo.name, html_url)

    def _list_merge_requests(self, repo: instarepo.github.Repo):
        head = self.github.auth.username + ":" + BRANCH_NAME
        return self.github.list_merge_requests(
            repo.full_name, head, repo.default_branch
        )

    def _close_mr_if_exists(self, repo: instarepo.github.Repo):
        merge_requests = self._list_merge_requests(repo)
        if not merge_requests:
            return
        merge_request = merge_requests[0]
        number = merge_request["number"]
        self.github.create_issue_comment(
            repo.full_name,
            number,
            "It seems the changes in this MR have already been fixed, auto-closing.",
        )
        self.github.close_merge_request(repo.full_name, number)

    def _auto_merge_existing_mr(self, repo: instarepo.github.Repo):
        merge_requests = self._list_merge_requests(repo)
        for merge_request in merge_requests:
            if self._auto_merge_one_existing_mr(repo, merge_request):
                return True
        return False

    def _auto_merge_one_existing_mr(self, repo: instarepo.github.Repo, merge_request):
        number = merge_request["number"]
        details = self.github.get_merge_request(repo.full_name, number)
        if not details["mergeable"]:
            logging.debug("Cannot merge MR because GitHub reports it is not mergeable")
            return False
        mergeable_state = details["mergeable_state"]
        if mergeable_state != "clean":
            logging.debug(
                "Cannot merge MR because the mergeable state is not clean but %s",
                mergeable_state,
            )
            return False
        head_sha = merge_request["head"]["sha"]
        check_runs = self.github.list_check_runs(repo.full_name, head_sha)
        if check_runs["total_count"] <= 0:
            logging.debug("Cannot merge MR because there are no check runs")
            return False
        for check_run in check_runs["check_runs"]:
            status = check_run["status"]
            if status != "completed":
                logging.debug("Cannot merge MR because there are incomplete check runs")
                return False
            conclusion = check_run["conclusion"]
            if conclusion != "success":
                logging.debug(
                    "Cannot merge MR because there are unsuccessful check runs"
                )
                return False

        self.github.merge_merge_request(repo.full_name, number)
        return True

    def _should_start_from_scratch(
        self, behind, ahead, git: instarepo.git.GitWorkingDir
    ):
        if self.force:
            logging.info("Force flag is set, starting branch from scratch")
            return True
        if behind > 0:
            logging.info(
                "Remote branch is behind default branch, starting from scratch"
            )
            return True
        if ahead > 0:
            author_names = git.get_author_names(f"origin/{BRANCH_NAME}")
            if len(author_names) != ahead:
                logging.warning(
                    "Found %d author names but expected %d", len(author_names), ahead
                )
                return False
            has_custom_authors = any(
                filter(lambda x: x != instarepo.git.AUTHOR_NAME, author_names)
            )
            if has_custom_authors:
                logging.info(
                    "Found commits by different authors, keeping existing branch"
                )
                return False
            logging.info("All commits are from instarepo, starting from scratch")
            return True
        logging.info("Existing branch has no commits")
        return False


def create_composite_fixer(fixer_classes, context: instarepo.fixers.context.Context):
    return instarepo.fixers.base.CompositeFix(
        list(
            map(
                lambda fixer_class: fixer_class(context),
                fixer_classes,
            )
        )
    )


def format_body(changes: Iterable[str]) -> str:
    body = "The following fixes have been applied:\n"
    for change in changes:
        lines = _non_empty_lines(change)
        first = True
        for line in lines:
            if first:
                body += "- "
                first = False
            else:
                body += "  "
            body += line + "\n"
    return body


def _non_empty_lines(value: str) -> Iterable[str]:
    lines = value.split("\n")
    stripped_lines = (line.strip() for line in lines)
    return (line for line in stripped_lines if line)


def epilog():
    """
    Creates a help text for the available fixers.
    """
    result = ""
    for clz in all_fixer_classes():
        result += fixer_class_to_fixer_key(clz)
        result += "\n    "
        result += clz.__doc__
        result += "\n"
    return result
