"""
Applies fixes to a repository that is either locally checked out
or remote on GitHub.
"""
import logging
import tempfile
from typing import Iterable, List

import instarepo.git
import instarepo.github
import instarepo.repo_source
import instarepo.fixers.base
import instarepo.fixers.changelog
import instarepo.fixers.ci
import instarepo.fixers.config
import instarepo.fixers.context
import instarepo.fixers.dotnet
import instarepo.fixers.license
import instarepo.fixers.maven
import instarepo.fixers.missing_files
import instarepo.fixers.pascal
import instarepo.fixers.readme
import instarepo.fixers.repo_description
import instarepo.fixers.vb6

from ..credentials import build_requests_auth


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
            if behind > 0:
                logging.info(
                    "Remote branch is behind default branch, starting from scratch"
                )
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


def try_get_fixer_order(fixer_class):
    return fixer_class.order if hasattr(fixer_class, "order") else 0


FIXER_PREFIX = "instarepo.fixers."
FIXER_SUFFIX = "Fix"


def fixer_class_to_fixer_key(clz):
    """
    Derives the unique fixer identifier out of a fixer class.
    The identifier is shorter and can be used to dynamically
    turn fixers on/off via the CLI.
    """
    full_module_name: str = clz.__module__
    expected_prefix = FIXER_PREFIX
    if not full_module_name.startswith(expected_prefix):
        raise ValueError(
            f"Module {full_module_name} did not start with prefix {expected_prefix}"
        )
    expected_suffix = FIXER_SUFFIX
    if not clz.__name__.endswith(expected_suffix):
        raise ValueError(
            f"Module {clz.__name__} did not end with suffix {expected_suffix}"
        )
    my_module = full_module_name[len(expected_prefix) :]
    return (
        my_module
        + "."
        + _pascal_case_to_underscore_case(clz.__name__[0 : -len(expected_suffix)])
    )


def _pascal_case_to_underscore_case(value: str) -> str:
    """
    Converts a pascal case string (e.g. MyClass)
    into a lower case underscore separated string (e.g. my_class).
    """
    result = ""
    state = "initial"
    partial = ""
    for char in value:
        if "A" <= char <= "Z":
            if state == "initial":
                state = "upper"
            elif state == "upper":
                state = "multi-upper"
            else:
                if result:
                    result += "_"
                result += partial
                partial = ""
                state = "upper"
            partial += char.lower()
        else:
            if state == "multi-upper":
                if result:
                    result += "_"
                result += partial
                partial = ""
            partial += char
            state = "lower"

    if result:
        result += "_"
    result += partial
    return result


def select_fixer_classes(
    only_fixers: List[str] = None, except_fixers: List[str] = None
):
    if only_fixers:
        if except_fixers:
            raise ValueError("Cannot use only_fixers and except_fixers together")
        unsorted_iterable = filter(
            lambda fixer_class: _fixer_class_starts_with_prefix(
                fixer_class, only_fixers
            ),
            all_fixer_classes(),
        )
    elif except_fixers:
        unsorted_iterable = filter(
            lambda fixer_class: not _fixer_class_starts_with_prefix(
                fixer_class, except_fixers
            ),
            all_fixer_classes(),
        )
    else:
        unsorted_iterable = all_fixer_classes()
    result = list(unsorted_iterable)
    result.sort(key=try_get_fixer_order)
    return result


def _fixer_class_starts_with_prefix(fixer_class, prefixes: List[str]):
    """
    Checks if the friendly name of the given fixer class starts with any of the given prefixes.
    """
    fixer_key = fixer_class_to_fixer_key(fixer_class)
    for prefix in prefixes:
        if fixer_key.startswith(prefix):
            return True
    return False


def all_fixer_classes():
    """Gets all fixer classes"""
    my_modules = [
        instarepo.fixers.changelog,
        instarepo.fixers.ci,
        instarepo.fixers.dotnet,
        instarepo.fixers.license,
        instarepo.fixers.maven,
        instarepo.fixers.missing_files,
        instarepo.fixers.pascal,
        instarepo.fixers.readme,
        instarepo.fixers.repo_description,
        instarepo.fixers.vb6,
    ]
    for my_module in my_modules:
        my_classes = classes_in_module(my_module)
        for clz in my_classes:
            if clz.__name__.endswith(FIXER_SUFFIX):
                yield clz


def classes_in_module(module):
    """
    Gets the classes defined in the given module
    """
    module_dict = module.__dict__
    return (
        module_dict[c]
        for c in module_dict
        if (
            isinstance(module_dict[c], type)
            and module_dict[c].__module__ == module.__name__
        )
    )
