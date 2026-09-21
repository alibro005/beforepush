import subprocess
from importlib.metadata import version

import pytest

import cli
from checks import CheckResult, CheckStatus


def test_cli_uses_main_by_default(monkeypatch):
    captured = {}

    def fake_run_checks(target, max_file_size):
        captured["target"] = target
        captured["max_file_size"] = max_file_size
        return []

    def fake_display_results(results, target):
        captured["results"] = results
        captured["display_target"] = target

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)

    monkeypatch.setattr(
        "sys.argv",
        ["beforepush"],
    )

    exit_code = cli.main()

    assert captured["target"] == "main"
    assert captured["max_file_size"] == 5 * 1024 * 1024
    assert captured["display_target"] == "main"
    assert captured["results"] == []
    assert exit_code == 0


def test_cli_accepts_custom_target(monkeypatch):
    captured = {}

    def fake_run_checks(target, max_file_size):
        captured["target"] = target
        captured["max_file_size"] = max_file_size
        return []

    def fake_display_results(results, target):
        captured["display_target"] = target

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)

    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "--target", "develop"],
    )

    cli.main()

    assert captured["target"] == "develop"
    assert captured["max_file_size"] == 5 * 1024 * 1024
    assert captured["display_target"] == "develop"


def test_cli_accepts_max_file_size(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target, max_file_size: (
            captured.update(max_file_size=max_file_size) or []
        ),
    )
    monkeypatch.setattr(cli, "display_results", lambda results, target: None)
    monkeypatch.setattr("sys.argv", ["beforepush", "--max-file-size", "10MB"])

    assert cli.main() == 0
    assert captured["max_file_size"] == 10 * 1024 * 1024


@pytest.mark.parametrize("value", ["abc", "5XYZ", "-5MB", "0", "1.1B"])
def test_cli_rejects_invalid_max_file_size(value, monkeypatch):
    monkeypatch.setattr("sys.argv", ["beforepush", "--max-file-size", value])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 2


@pytest.mark.parametrize("branch", ["main", "feature/test"])
def test_cli_without_commits(tmp_path, monkeypatch, capsys, branch):
    subprocess.run(
        ["git", "init", "--initial-branch", branch, str(tmp_path)],
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 1

    output = capsys.readouterr().out
    assert "Commit history" in output
    assert "no commits" in output
    assert "NOT READY" in output
    assert "Upstream branch" not in output
    assert "Target branch" not in output


def test_cli_with_initial_commit(tmp_path, monkeypatch, capsys):
    subprocess.run(
        ["git", "init", "--initial-branch", "main", str(tmp_path)],
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--allow-empty",
            "-m",
            "Initial commit",
        ],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0

    output = capsys.readouterr().out
    assert "no commits" not in output
    assert "Working tree is clean." in output
    assert "No upstream branch configured." in output
    assert "Currently on target branch 'main'." in output


def test_cli_returns_zero_when_checks_pass(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target, max_file_size: [
            CheckResult("Example", CheckStatus.PASS, "Passed."),
        ],
    )
    monkeypatch.setattr(cli, "display_results", lambda results, target: None)
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0


def test_cli_returns_zero_when_checks_only_warn(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target, max_file_size: [
            CheckResult("Example", CheckStatus.WARNING, "Warning."),
        ],
    )
    monkeypatch.setattr(cli, "display_results", lambda results, target: None)
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0


def test_cli_returns_nonzero_when_check_fails(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target, max_file_size: [
            CheckResult("Example", CheckStatus.FAIL, "Failed."),
        ],
    )
    monkeypatch.setattr(cli, "display_results", lambda results, target: None)
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 1


def test_cli_version(capsys, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "--version"],
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == (f"beforepush {version('before-push')}")


def test_cli_install_hook(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "install_pre_push_hook",
        lambda: "BeforePush pre-push hook installed.",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "install-hook"],
    )

    assert cli.main() == 0
    assert "installed" in capsys.readouterr().out.lower()


def test_cli_uninstall_hook(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "uninstall_pre_push_hook",
        lambda: "BeforePush pre-push hook removed.",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "uninstall-hook"],
    )

    assert cli.main() == 0
    assert "removed" in capsys.readouterr().out.lower()


def test_cli_install_hook_error(monkeypatch, capsys):
    def fail_install():
        raise RuntimeError("Not inside a Git repository.")

    monkeypatch.setattr(cli, "install_pre_push_hook", fail_install)
    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "install-hook"],
    )

    assert cli.main() == 1

    error = capsys.readouterr().err
    assert "Not inside a Git repository." in error
