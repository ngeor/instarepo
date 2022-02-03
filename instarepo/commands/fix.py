import logging
import tempfile
from typing import Iterable, List

import instarepo.git
import instarepo.github
import instarepo.repo_source
import instarepo.fixers.base
import instarepo.fixers.changelog
import instarepo.fixers.ci
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
    def __init__(self, args):
        if args.dry_run:
            self.github = instarepo.github.GitHub(auth=build_requests_auth(args))
        else:
            self.github = instarepo.github.ReadWriteGitHub(
                auth=build_requests_auth(args)
            )
        self.repo_source = (
            instarepo.repo_source.RepoSourceBuilder()
            .with_github(self.github)
            .with_args(args)
            .build()
        )
        self.dry_run: bool = args.dry_run
        self.verbose: bool = args.verbose
        self.fixer_classes = list(
            select_fixer_classes(args.only_fixers, args.except_fixers)
        )
        self.fixer_classes.sort(key=try_get_fixer_order)

    def run(self):
        if not self.fixer_classes:
            logging.error("No fixers selected!")
            return
        logging.debug(
            "Using fixers %s",
            ", ".join(map(fixer_class_to_fixer_key, self.fixer_classes)),
        )
        repos = self.repo_source.get()
        for repo in repos:
            self.process(repo)

    def process(self, repo: instarepo.github.Repo):
        logging.info("Processing repo %s", repo.name)
        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug("Cloning repo into temp dir %s", tmpdirname)
            git = instarepo.git.clone(repo.ssh_url, tmpdirname, quiet=not self.verbose)
            processor = RepoProcessor(
                repo, self.github, git, self.fixer_classes, self.dry_run, self.verbose
            )
            processor.process()


class RepoProcessor:
    def __init__(
        self,
        repo: instarepo.github.Repo,
        github: instarepo.github.GitHub,
        git: instarepo.git.GitWorkingDir,
        fixer_classes,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        self.repo = repo
        self.github = github
        self.git = git
        self.fixer_classes = fixer_classes
        self.dry_run = dry_run
        self.branch_name = "instarepo_branch"
        self.verbose = verbose

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
        remote_branch_sha = ""
        try:
            remote_branch_sha = self.git.rev_parse(f"remotes/origin/{self.branch_name}")
        except:  # pylint: disable=bare-except
            pass
        if remote_branch_sha:
            self.git.checkout(self.branch_name)
        else:
            self.git.create_branch(self.branch_name)

    def run_fixes(self):
        composite_fixer = self._create_composite_fixer()
        return composite_fixer.run()

    def _create_composite_fixer(self):
        return instarepo.fixers.base.CompositeFix(
            list(
                map(
                    self._create_fixer,
                    self.fixer_classes,
                )
            )
        )

    def _create_fixer(self, fixer_class):
        return fixer_class(
            git=self.git, repo=self.repo, github=self.github, verbose=self.verbose
        )

    def has_changes(self):
        current_sha = self.git.rev_parse(self.branch_name)
        main_sha = self.git.rev_parse(self.repo.default_branch)
        return current_sha != main_sha

    def create_merge_request(self, changes: Iterable[str]):
        if self.dry_run:
            logging.info("Would have created PR for repo %s", self.repo.name)
            return
        self.git.push()
        if self.github.has_merge_request(
            self.repo.full_name, self.branch_name, self.repo.default_branch
        ):
            logging.info("PR already exists for repo %s", self.repo.name)
        else:
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


def non_empty_lines(value: str) -> Iterable[str]:
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
    try:
        return fixer_class.order
    except:
        return 0


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
        + pascal_case_to_underscore_case(clz.__name__[0 : -len(expected_suffix)])
    )


def pascal_case_to_underscore_case(value: str) -> str:
    """
    Converts a pascal case string (e.g. MyClass)
    into a lower case underscore separated string (e.g. my_class).
    """
    result = ""
    for ch in value:
        if "A" <= ch <= "Z":
            if result:
                result += "_"
            result += ch.lower()
        else:
            result += ch
    return result


def select_fixer_classes(
    only_fixers: List[str] = None, except_fixers: List[str] = None
):
    if only_fixers:
        if except_fixers:
            raise ValueError("Cannot use only_fixers and except_fixers together")
        return filter(
            lambda fixer_class: fixer_class_starts_with_prefix(
                fixer_class, only_fixers
            ),
            all_fixer_classes(),
        )
    elif except_fixers:
        return filter(
            lambda fixer_class: not fixer_class_starts_with_prefix(
                fixer_class, except_fixers
            ),
            all_fixer_classes(),
        )
    else:
        return all_fixer_classes()


def fixer_class_starts_with_prefix(fixer_class, prefixes: List[str]):
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
