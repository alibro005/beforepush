import os
import shutil
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


def test_get_git_dir(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    assert git.get_git_dir() == (tmp_path / ".git").resolve()


def test_get_hooks_dir(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    assert git.get_hooks_dir() == (tmp_path / ".git" / "hooks").resolve()


def test_get_hooks_dir_from_subdirectory(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    subdirectory = tmp_path / "src" / "app"
    subdirectory.mkdir(parents=True)

    monkeypatch.chdir(subdirectory)

    assert git.get_git_dir() == (tmp_path / ".git").resolve()
    assert git.get_hooks_dir() == (tmp_path / ".git" / "hooks").resolve()


def test_get_git_dir_outside_repository(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RuntimeError, match="Not inside a Git repository."):
        git.get_git_dir()


def test_is_beforepush_hook(tmp_path):
    hook = tmp_path / "pre-push"

    hook.write_text(
        "#!/bin/sh\n# Installed by BeforePush\nbeforepush\nexit $?\n",
        encoding="utf-8",
    )

    assert git.is_beforepush_hook(hook)


def test_is_not_beforepush_hook(tmp_path):
    hook = tmp_path / "pre-push"

    hook.write_text(
        "#!/bin/sh\nsome-other-tool\n",
        encoding="utf-8",
    )

    assert not git.is_beforepush_hook(hook)


def test_install_pre_push_hook(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    message = git.install_pre_push_hook()

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"

    assert hook_path.exists()
    assert git.is_beforepush_hook(hook_path)
    assert "beforepush" in hook_path.read_text(encoding="utf-8")
    assert "Installed by BeforePush" in hook_path.read_text(encoding="utf-8")
    assert "installed" in message.lower()


def test_install_pre_push_hook_is_idempotent(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    git.install_pre_push_hook()

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    original_content = hook_path.read_text(encoding="utf-8")

    message = git.install_pre_push_hook()

    assert hook_path.read_text(encoding="utf-8") == original_content
    assert "already installed" in message.lower()


def test_uninstall_pre_push_hook(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    git.install_pre_push_hook()

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    assert hook_path.exists()

    message = git.uninstall_pre_push_hook()

    assert not hook_path.exists()
    assert "removed" in message.lower()


def test_uninstall_pre_push_hook_when_not_installed(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    message = git.uninstall_pre_push_hook()

    assert "not installed" in message.lower()


def test_uninstall_pre_push_hook_does_not_remove_existing_hook(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"
    existing_content = "#!/bin/sh\nsome-other-hook\n"
    hook_path.write_text(existing_content, encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    message = git.uninstall_pre_push_hook()

    assert hook_path.exists()
    assert hook_path.read_text(encoding="utf-8") == existing_content
    assert "not removed" in message.lower()


@pytest.mark.skipif(shutil.which("sh") is None, reason="sh is required")
def test_installed_hook_propagates_beforepush_exit_code(tmp_path, monkeypatch):
    subprocess.run(
        ["git", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    monkeypatch.chdir(tmp_path)

    git.install_pre_push_hook()

    hook_path = tmp_path / ".git" / "hooks" / "pre-push"

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    fake_beforepush = fake_bin / "beforepush"
    fake_beforepush.write_text(
        "#!/bin/sh\nexit 7\n",
        encoding="utf-8",
    )
    fake_beforepush.chmod(fake_beforepush.stat().st_mode | 0o111)

    monkeypatch.setenv(
        "PATH",
        f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
    )

    result = subprocess.run(
        ["sh", str(hook_path)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 7
