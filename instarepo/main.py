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
        "-u", "--user", action="store", required=True, help="The GitHub username"
    )
    parser.add_argument(
        "-t", "--token", action="store", required=True, help="The GitHub token"
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
    parser.add_argument(
        "--sort",
        action="store",
        default="full_name",
        choices=["full_name", "created", "updated", "pushed"],
    )
    parser.add_argument(
        "--direction", action="store", default="asc", choices=["asc", "desc"]
    )

    subparsers = parser.add_subparsers(
        dest="subparser_name", help="Sub-commands help", required=True
    )

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyzes the available repositories, counting historical LOC"
    )
    analyze_parser.add_argument(
        "--since", required=True, action="store", help="The start date of the analysis (YYYY-mm-dd)"
    )
    analyze_parser.add_argument(
        "--metric",
        choices=["commits", "files"],
        default="commits",
        help="The metric to report on",
    )

    subparsers.add_parser("list", help="Lists the available repositories")

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
