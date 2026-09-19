import os
import subprocess


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


def get_current_branch() -> str:
    """Get the current branch name."""
    return run_git_command("branch", "--show-current")


def get_status() -> str:
    """Get the repository status in porcelain format."""
    return run_git_command("status", "--porcelain")


def get_staged_added_files() -> list[tuple[str, int]]:
    """Return paths and blob sizes for files newly added to the Git index."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--diff-filter=A", "--name-only", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace").strip())

    paths = os.fsdecode(result.stdout)
    files = []
    for path in paths.split("\0"):
        if not path:
            continue
        size_result = subprocess.run(
            ["git", "cat-file", "-s", f":0:{path}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if size_result.returncode != 0:
            raise RuntimeError(size_result.stderr.strip())
        files.append((path, int(size_result.stdout.strip())))
    return files


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
