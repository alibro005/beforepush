import git
from checks import (
    CheckStatus,
    check_current_branch,
    check_git_repository,
    check_target_branch,
    check_upstream_branch,
    check_working_tree,
)


def test_git_repository_pass(monkeypatch):
    monkeypatch.setattr(git, "is_git_repository", lambda: True)

    result = check_git_repository()

    assert result.status == CheckStatus.PASS
    assert result.name == "Git repository"


def test_git_repository_fail(monkeypatch):
    monkeypatch.setattr(git, "is_git_repository", lambda: False)

    result = check_git_repository()

    assert result.status == CheckStatus.FAIL
    assert result.name == "Git repository"


def test_current_branch_pass(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "feature/test",
    )

    result = check_current_branch()

    assert result.status == CheckStatus.PASS
    assert "feature/test" in result.message


def test_current_branch_fail(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "",
    )

    result = check_current_branch()

    assert result.status == CheckStatus.FAIL
    assert "No branch" in result.message


def test_working_tree_clean(monkeypatch):
    monkeypatch.setattr(git, "has_changes", lambda: False)

    result = check_working_tree()

    assert result.status == CheckStatus.PASS
    assert "clean" in result.message


def test_working_tree_has_changes(monkeypatch):
    monkeypatch.setattr(git, "has_changes", lambda: True)

    result = check_working_tree()

    assert result.status == CheckStatus.FAIL
    assert "changes detected" in result.message


def test_upstream_branch_pass(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_upstream_branch",
        lambda: "origin/main",
    )

    result = check_upstream_branch()

    assert result.status == CheckStatus.PASS
    assert "origin/main" in result.message


def test_upstream_branch_warning(monkeypatch):
    def raise_error():
        raise RuntimeError("No upstream")

    monkeypatch.setattr(
        git,
        "get_upstream_branch",
        raise_error,
    )

    result = check_upstream_branch()

    assert result.status == CheckStatus.WARNING
    assert "No upstream branch" in result.message


def test_target_branch_current(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "main",
    )

    result = check_target_branch("main")

    assert result.status == CheckStatus.PASS
    assert "target branch 'main'" in result.message


def test_target_branch_up_to_date(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "feature/test",
    )
    monkeypatch.setattr(
        git,
        "branch_exists",
        lambda target: True,
    )
    monkeypatch.setattr(
        git,
        "get_behind_count",
        lambda target: 0,
    )

    result = check_target_branch("main")

    assert result.status == CheckStatus.PASS
    assert "up to date" in result.message


def test_target_branch_behind_one_commit(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "feature/test",
    )
    monkeypatch.setattr(
        git,
        "branch_exists",
        lambda target: True,
    )
    monkeypatch.setattr(
        git,
        "get_behind_count",
        lambda target: 1,
    )

    result = check_target_branch("main")

    assert result.status == CheckStatus.FAIL
    assert "1 commit behind main" in result.message


def test_target_branch_behind_multiple_commits(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "feature/test",
    )
    monkeypatch.setattr(
        git,
        "branch_exists",
        lambda target: True,
    )
    monkeypatch.setattr(
        git,
        "get_behind_count",
        lambda target: 3,
    )

    result = check_target_branch("main")

    assert result.status == CheckStatus.FAIL
    assert "3 commits behind main" in result.message


def test_target_branch_missing(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "feature/test",
    )
    monkeypatch.setattr(
        git,
        "branch_exists",
        lambda target: False,
    )

    result = check_target_branch("develop")

    assert result.status == CheckStatus.FAIL
    assert result.message == "Target branch 'develop' does not exist."


def test_target_branch_compare_error_preserved(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_current_branch",
        lambda: "feature/test",
    )
    monkeypatch.setattr(
        git,
        "branch_exists",
        lambda target: True,
    )

    def raise_error(target):
        raise RuntimeError("ambiguous argument")

    monkeypatch.setattr(git, "get_behind_count", raise_error)

    result = check_target_branch("main")

    assert result.status == CheckStatus.FAIL
    assert result.message == "Could not compare with 'main'."
