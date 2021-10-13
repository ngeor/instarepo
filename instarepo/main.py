import argparse
import logging

import instarepo.commands.fix


def main():
    args = parse_args()
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )
    if args.subparser_name == "fix":
        main = instarepo.commands.fix.Main(args)
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

    subparsers = parser.add_subparsers(
        dest="subparser_name", help="Sub-commands help", required=True
    )
    list_parser = subparsers.add_parser("list", help="Lists the available repositories")
    fix_parser = subparsers.add_parser(
        "fix",
        description="Runs automatic fixes on the repositories",
        help="Runs automatic fixes on the repositories",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
