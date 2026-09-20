import argparse
import sys
from importlib.metadata import version

from checks import CheckStatus, run_checks
from git import install_pre_push_hook, uninstall_pre_push_hook
from output import display_results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether your Git branch is ready before pushing or opening a PR."
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["install-hook", "uninstall-hook"],
        help="Install or uninstall the BeforePush pre-push hook.",
    )

    parser.add_argument(
        "--target",
        default="main",
        help="Target branch to compare against (default: main)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"beforepush {version('before-push')}",
    )

    args = parser.parse_args()

    if args.command == "install-hook":
        try:
            print(install_pre_push_hook())
        except RuntimeError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        return 0

    if args.command == "uninstall-hook":
        try:
            print(uninstall_pre_push_hook())
        except RuntimeError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        return 0

    results = run_checks(args.target)
    display_results(results, args.target)

    return int(any(result.status == CheckStatus.FAIL for result in results))


if __name__ == "__main__":
    sys.exit(main())
