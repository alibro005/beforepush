from dataclasses import dataclass
from enum import Enum

import git


class CheckStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


# Check result data class
@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str


def check_git_repository() -> CheckResult:
    """Check whether the current directory is a Git repository."""
    if git.is_git_repository():
        return CheckResult(
            name="Git repository",
            status=CheckStatus.PASS,
            message="Current directory is a Git repository.",
        )

    return CheckResult(
        name="Git repository",
        status=CheckStatus.FAIL,
        message="Current directory is not a Git repository.",
    )


def check_current_branch() -> CheckResult:
    """Check whether a branch is currently checked out."""
    try:
        branch = git.get_current_branch()
    except RuntimeError:
        return CheckResult(
            name="Current branch",
            status=CheckStatus.FAIL,
            message="Could not determine the current branch.",
        )

    if branch:
        return CheckResult(
            name="Current branch",
            status=CheckStatus.PASS,
            message=f"Currently on '{branch}'.",
        )

    return CheckResult(
        name="Current branch",
        status=CheckStatus.FAIL,
        message="No branch is currently checked out.",
    )


def check_working_tree() -> CheckResult:
    """Check whether the working tree is clean."""
    try:
        has_changes = git.has_changes()
    except RuntimeError:
        return CheckResult(
            name="Working tree",
            status=CheckStatus.FAIL,
            message="Could not read the Git working tree.",
        )

    if not has_changes:
        return CheckResult(
            name="Working tree",
            status=CheckStatus.PASS,
            message="Working tree is clean.",
        )

    return CheckResult(
        name="Working tree",
        status=CheckStatus.FAIL,
        message="Uncommitted or untracked changes detected.",
    )


def check_upstream_branch() -> CheckResult:
    """Check whether the current branch has an upstream branch."""
    try:
        upstream = git.get_upstream_branch()
    except RuntimeError:
        return CheckResult(
            name="Upstream branch",
            status=CheckStatus.WARNING,
            message="No upstream branch configured.",
        )

    return CheckResult(
        name="Upstream branch",
        status=CheckStatus.PASS,
        message=f"Tracking '{upstream}'.",
    )


def check_target_branch(target: str) -> CheckResult:
    """Check whether the current branch is behind the target branch."""
    try:
        current_branch = git.get_current_branch()

        if current_branch == target:
            return CheckResult(
                name="Target branch",
                status=CheckStatus.PASS,
                message=f"Currently on target branch '{target}'.",
            )

        if not git.branch_exists(target):
            return CheckResult(
                name="Target branch",
                status=CheckStatus.FAIL,
                message=f"Target branch '{target}' does not exist.",
            )

        behind = git.get_behind_count(target)

    except RuntimeError:
        return CheckResult(
            name="Target branch",
            status=CheckStatus.FAIL,
            message=f"Could not compare with '{target}'.",
        )

    if behind == 0:
        return CheckResult(
            name="Target branch",
            status=CheckStatus.PASS,
            message=f"Branch is up to date with {target}.",
        )
    commit_word = "commit" if behind == 1 else "commits"
    return CheckResult(
        name="Target branch",
        status=CheckStatus.FAIL,
        message=f"Branch is {behind} {commit_word} behind {target}. "
        f"Update your branch before opening a PR.",
    )


def run_checks(target: str) -> list[CheckResult]:
    """Run all repository readiness checks."""
    repository = check_git_repository()
    if repository.status == CheckStatus.PASS and not git.branch_exists("HEAD"):
        return [
            repository,
            CheckResult(
                name="Commit history",
                status=CheckStatus.FAIL,
                message="Current branch has no commits to check. "
                "Create a commit before checking readiness.",
            ),
        ]

    return [
        repository,
        check_current_branch(),
        check_working_tree(),
        check_upstream_branch(),
        check_target_branch(target),
    ]
