import subprocess

import pytest

import git


def test_run_git_command_success(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["git", "status"],
            returncode=0,
            stdout="clean",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = git.run_git_command("status")

    assert result == "clean"


def test_run_git_command_failure(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["git", "status"],
            returncode=1,
            stdout="",
            stderr="fatal: not a git repository",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="not a git repository"):
        git.run_git_command("status")


def test_is_git_repository_true(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["git", "rev-parse"],
            returncode=0,
            stdout="true\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert git.is_git_repository() is True


def test_is_git_repository_false(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["git", "rev-parse"],
            returncode=128,
            stdout="",
            stderr="fatal: not a git repository",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert git.is_git_repository() is False


def test_get_current_branch(monkeypatch):
    monkeypatch.setattr(
        git,
        "run_git_command",
        lambda *args: "feature/test",
    )

    assert git.get_current_branch() == "feature/test"


def test_get_status(monkeypatch):
    monkeypatch.setattr(
        git,
        "run_git_command",
        lambda *args: "M src/checks.py",
    )

    assert git.get_status() == "M src/checks.py"


def test_has_changes_true(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_status",
        lambda: " M src/checks.py",
    )

    assert git.has_changes() is True


def test_has_changes_false(monkeypatch):
    monkeypatch.setattr(
        git,
        "get_status",
        lambda: "",
    )

    assert git.has_changes() is False


def test_get_upstream_branch(monkeypatch):
    monkeypatch.setattr(
        git,
        "run_git_command",
        lambda *args: "origin/main",
    )

    assert git.get_upstream_branch() == "origin/main"


def test_get_behind_count(monkeypatch):
    monkeypatch.setattr(
        git,
        "run_git_command",
        lambda *args: "3",
    )

    assert git.get_behind_count("main") == 3


def test_branch_exists_true(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["git", "rev-parse"],
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert git.branch_exists("main") is True


def test_branch_exists_false(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["git", "rev-parse"],
            returncode=1,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert git.branch_exists("develop") is False
