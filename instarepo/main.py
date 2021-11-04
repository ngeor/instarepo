import argparse
import logging

import instarepo.commands.analyze
import instarepo.commands.fix
import instarepo.commands.list


def main():
    args = parse_args()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    if args.subparser_name == "analyze":
        cmd = instarepo.commands.analyze.AnalyzeCommand(args)
    elif args.subparser_name == "fix":
        cmd = instarepo.commands.fix.FixCommand(args)
    elif args.subparser_name == "list":
        cmd = instarepo.commands.list.ListCommand(args)
    else:
        raise ValueError(f"Sub-parser {args.subparser_name} is not implemented")
    cmd.run()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Apply changes on multiple repositories"
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Verbose output"
    )

    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "-u", "--user", action="store", required=True, help="The GitHub username"
    )
    auth_group.add_argument(
        "-t", "--token", action="store", required=True, help="The GitHub token"
    )

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

    language_group = parser.add_mutually_exclusive_group()
    language_group.add_argument(
        "--only-language",
        action="store",
        help="Only process repositories of the given programming language",
    )
    language_group.add_argument(
        "--except-language",
        action="store",
        help="Do not process repositories of the given programming language",
    )

    prefix_group = parser.add_mutually_exclusive_group()
    prefix_group.add_argument(
        "--only-name-prefix",
        action="store",
        help="Only process repositories whose name starts with the given prefix",
    )
    prefix_group.add_argument(
        "--except-name-prefix",
        action="store",
        help="Do not process repositories whose name starts with the given prefix",
    )

    filter_group = parser.add_argument_group("Filtering")

    filter_group.add_argument(
        "--forks",
        action="store",
        default="deny",
        choices=["allow", "deny", "only"],
        help="Filter forks",
    )

    subparsers = parser.add_subparsers(
        dest="subparser_name", help="Sub-commands help", required=True
    )

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyzes the available repositories, counting historical LOC"
    )
    analyze_parser.add_argument(
        "--since",
        required=True,
        action="store",
        help="The start date of the analysis (YYYY-mm-dd)",
    )
    analyze_parser.add_argument(
        "--metric",
        choices=["commits", "files"],
        default="commits",
        help="The metric to report on",
    )
    analyze_parser.add_argument(
        "--archived",
        action="store",
        default="deny",
        choices=["allow", "deny", "only"],
        help="Filter archived repositories",
    )

    list_parser = subparsers.add_parser("list", help="Lists the available repositories")
    list_parser.add_argument(
        "--archived",
        action="store",
        default="deny",
        choices=["allow", "deny", "only"],
        help="Filter archived repositories",
    )

    fix_parser = subparsers.add_parser(
        "fix",
        description="Runs automatic fixes on the repositories",
        help="Runs automatic fixes on the repositories",
    )
    fix_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Do not actually push and create MR",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
