import subprocess
from pathlib import Path

BEFOREPUSH_HOOK_MARKER = "# Installed by BeforePush"

BEFOREPUSH_HOOK_CONTENT = """#!/bin/sh
# Installed by BeforePush
beforepush
exit $?
"""


def run_git_command(*args: str) -> str:
    """Run a Git command and return its output."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


def is_git_repository() -> bool:
    """Check whether the current directory is a Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0 and result.stdout.strip() == "true"


def get_git_dir() -> Path:
    """Return the path to the repository's Git directory."""
    try:
        return Path(run_git_command("rev-parse", "--git-dir")).resolve()
    except RuntimeError:
        raise RuntimeError("Not inside a Git repository.") from None


def get_hooks_dir() -> Path:
    """Return the repository's configured Git hooks directory."""
    return Path(run_git_command("rev-parse", "--git-path", "hooks")).resolve()


def get_current_branch() -> str:
    """Get the current branch name."""
    return run_git_command("branch", "--show-current")


def get_status() -> str:
    """Get the repository status in porcelain format."""
    return run_git_command("status", "--porcelain")


def has_changes() -> bool:
    """Check whether the working tree contains changes."""
    return bool(get_status())


def get_upstream_branch() -> str:
    """Get the upstream branch configured for the current branch."""
    return run_git_command(
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{u}",
    )


def get_behind_count(target: str) -> int:
    """Return the number of commits the current branch is behind the target."""
    output = run_git_command(
        "rev-list",
        "--count",
        f"HEAD..{target}",
    )

    return int(output)


def branch_exists(name: str) -> bool:
    """Return whether a Git ref that resolves to a commit exists."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{name}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def is_beforepush_hook(hook_path: Path) -> bool:
    """Return whether the hook was installed by BeforePush."""
    if not hook_path.is_file():
        return False

    return BEFOREPUSH_HOOK_MARKER in hook_path.read_text(encoding="utf-8")


def install_pre_push_hook() -> str:
    """Install the BeforePush pre-push hook."""
    hooks_dir = get_hooks_dir()
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hooks_dir / "pre-push"

    if hook_path.exists():
        if is_beforepush_hook(hook_path):
            return "BeforePush pre-push hook is already installed."

        return (
            f"An existing pre-push hook was found at {hook_path}. No changes were made."
        )

    hook_path.write_text(BEFOREPUSH_HOOK_CONTENT, encoding="utf-8")

    # Make the hook executable without changing unrelated permission bits.
    hook_path.chmod(hook_path.stat().st_mode | 0o111)

    return f"BeforePush pre-push hook installed at {hook_path}."


def uninstall_pre_push_hook() -> str:
    """Remove the BeforePush pre-push hook if installed."""
    hooks_dir = get_hooks_dir()
    hook_path = hooks_dir / "pre-push"

    if not hook_path.exists():
        return "BeforePush pre-push hook is not installed."

    if not is_beforepush_hook(hook_path):
        return (
            f"An existing pre-push hook was found at {hook_path}. It was not removed."
        )

    hook_path.unlink()

    return f"BeforePush pre-push hook removed from {hook_path}."
