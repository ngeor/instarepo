"""Main entrypoint of the program"""
import argparse
import logging

import instarepo
import instarepo.commands.analyze
import instarepo.commands.clone
import instarepo.commands.fix
import instarepo.commands.list
import instarepo.commands.login
import instarepo.commands.logout


def main():
    """Main entrypoint of the program"""
    args = parse_args()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    cmd = create_command(args)
    cmd.run()


def create_command(args):
    """Creates the command handler for the given parsed CLI arguments"""
    if args.subparser_name == "analyze":
        cmd = instarepo.commands.analyze.AnalyzeCommand(args)
    elif args.subparser_name == "fix":
        cmd = instarepo.commands.fix.FixCommand(args)
    elif args.subparser_name == "list":
        cmd = instarepo.commands.list.ListCommand(args)
    elif args.subparser_name == "clone":
        cmd = instarepo.commands.clone.CloneCommand(args)
    elif args.subparser_name == "login":
        cmd = instarepo.commands.login.LoginCommand(args)
    elif args.subparser_name == "logout":
        cmd = instarepo.commands.logout.LogoutCommand(args)
    else:
        raise ValueError(f"Sub-parser {args.subparser_name} is not implemented")
    return cmd


def parse_args(args=None):
    """Parses the CLI arguments"""
    parser = argparse.ArgumentParser(
        description="Apply changes on multiple repositories", prog="instarepo"
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Verbose output"
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + instarepo.__version__
    )

    subparsers = parser.add_subparsers(
        dest="subparser_name", help="Sub-commands help", required=True
    )

    list_parser = subparsers.add_parser(
        "list",
        help="Lists the available repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
    instarepo list -u USER -t TOKEN
    """,
    )
    _configure_list_parser(list_parser)

    fix_parser = subparsers.add_parser(
        "fix",
        description="Runs automatic fixes on the repositories",
        help="Runs automatic fixes on the repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
    instarepo fix -u USER -t TOKEN

Fixers:

"""
        + instarepo.commands.fix.epilog(),
    )
    _configure_fix_parser(fix_parser)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyzes the available repositories, counting historical LOC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
    instarepo analyze -u USER -t TOKEN --since 2021-11-06
    """,
    )
    _configure_analyze_parser(analyze_parser)

    clone_parser = subparsers.add_parser(
        "clone",
        help="Clones all the available repositories",
    )
    _configure_clone_parser(clone_parser)

    login_parser = subparsers.add_parser(
        "login",
        help="Provide GitHub credentials for subsequent commands",
    )
    _configure_login_parser(login_parser)

    subparsers.add_parser(
        "logout",
        help="Delete previously stored GitHub credentials",
    )

    return parser.parse_args(args)


def _configure_list_parser(parser: argparse.ArgumentParser):
    _add_auth_options(parser)
    _add_sort_options(parser)
    _add_filter_options(parser)
    _add_archived_option(parser)


def _configure_fix_parser(parser: argparse.ArgumentParser):
    _add_auth_options(parser)
    _add_sort_options(parser)
    _add_filter_options(parser)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Do not actually push and create MR",
    )
    fixer_group = parser.add_mutually_exclusive_group()
    fixer_group.add_argument(
        "--only-fixers",
        action="store",
        nargs="+",
        help="Only run fixers that have the given prefixes",
    )
    fixer_group.add_argument(
        "--except-fixers",
        action="store",
        nargs="+",
        help="Do not run fixers that have the given prefixes",
    )
    parser.add_argument(
        "--local-dir",
        help="Apply fixes for a project at a local working directory. Skips all GitHub related calls and git push.",
    )
    parser.add_argument(
        "--auto-merge",
        action="store_true",
        default=False,
        help="Automatically merge open MRs that pass CI.",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        required=False,
        help="The location of an optional configuration file",
    )


def _configure_analyze_parser(parser: argparse.ArgumentParser):
    _add_auth_options(parser)
    _add_sort_options(parser)
    _add_filter_options(parser)
    _add_archived_option(parser)
    parser.add_argument(
        "--since",
        required=True,
        action="store",
        help="The start date of the analysis (YYYY-mm-dd)",
    )
    parser.add_argument(
        "--metric",
        choices=["commits", "files"],
        default="commits",
        help="The metric to report on",
    )


def _configure_clone_parser(parser: argparse.ArgumentParser):
    _add_auth_options(parser)
    _add_archived_option(parser)
    _add_filter_options(parser)
    parser.add_argument(
        "--projects-dir",
        required=True,
        help="The directory where projects are going to be cloned into",
    )


def _configure_login_parser(parser: argparse.ArgumentParser):
    _add_auth_options(parser, required=True)


def _add_archived_option(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--archived",
        action="store",
        default="deny",
        choices=["allow", "deny", "only"],
        help="Filter archived repositories",
    )


def _add_auth_options(parser: argparse.ArgumentParser, required=False):
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "-u", "--username", required=required, help="The GitHub username"
    )
    auth_group.add_argument("-t", "--token", required=required, help="The GitHub token")


def _add_sort_options(parser: argparse.ArgumentParser):
    sort_group = parser.add_argument_group("Sorting")
    sort_group.add_argument(
        "--sort",
        action="store",
        default="full_name",
        choices=["full_name", "created", "updated", "pushed"],
    )
    sort_group.add_argument(
        "--direction", action="store", default="asc", choices=["asc", "desc"]
    )


def _add_filter_options(parser: argparse.ArgumentParser):
    language_group = parser.add_mutually_exclusive_group()
    language_group.add_argument(
        "--only-language",
        help="Only process repositories of the given programming language",
    )
    language_group.add_argument(
        "--except-language",
        help="Do not process repositories of the given programming language",
    )

    prefix_group = parser.add_mutually_exclusive_group()
    prefix_group.add_argument(
        "--only-name-prefix",
        help="Only process repositories whose name starts with the given prefix",
    )
    prefix_group.add_argument(
        "--except-name-prefix",
        help="Do not process repositories whose name starts with the given prefix",
    )

    filter_group = parser.add_argument_group("Filtering")

    filter_group.add_argument(
        "--forks",
        default="deny",
        choices=["allow", "deny", "only"],
        help="Filter forks",
    )
    filter_group.add_argument(
        "--pushed-after",
        help="Only process repositories that had changes pushed after the given time interval e.g. 4h",
    )
    filter_group.add_argument(
        "--pushed-before",
        help="Only process repositories that had changes pushed before the given time interval e.g. 4h",
    )


if __name__ == "__main__":
    main()
