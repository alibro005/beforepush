import argparse
import sys
from importlib.metadata import version

from checks import CheckStatus, run_checks
from output import display_results
from sizes import format_file_size, parse_file_size


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether your Git branch is ready before pushing or opening a PR."
    )

    parser.add_argument(
        "--target",
        default="main",
        help="Target branch to compare against (default: main)",
    )

    parser.add_argument(
        "--max-file-size",
        type=parse_file_size,
        default=5 * 1024 * 1024,
        metavar="SIZE",
        help=(
            "Warn about newly staged files larger than SIZE "
            f"(default: {format_file_size(5 * 1024 * 1024)}; supports bytes, KB, or MB)"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"beforepush {version('before-push')}",
    )

    args = parser.parse_args()

    results = run_checks(args.target, args.max_file_size)
    display_results(results, args.target)

    return int(any(result.status == CheckStatus.FAIL for result in results))


if __name__ == "__main__":
    sys.exit(main())
