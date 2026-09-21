import subprocess
from importlib.metadata import version

import pytest

import cli
import output
from checks import CheckResult, CheckStatus


def test_cli_uses_main_by_default(monkeypatch):
    captured = {}

    def fake_run_checks(target):
        captured["target"] = target
        return []

    def fake_display_results(results, target, *, verbose=False):
        captured["results"] = results
        captured["display_target"] = target
        captured["verbose"] = verbose

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)

    monkeypatch.setattr(
        "sys.argv",
        ["beforepush"],
    )

    exit_code = cli.main()

    assert captured["target"] == "main"
    assert captured["display_target"] == "main"
    assert captured["results"] == []
    assert captured["verbose"] is False
    assert exit_code == 0


def test_cli_accepts_custom_target(monkeypatch):
    captured = {}

    def fake_run_checks(target):
        captured["target"] = target
        return []

    def fake_display_results(results, target, *, verbose=False):
        captured["display_target"] = target

    monkeypatch.setattr(cli, "run_checks", fake_run_checks)
    monkeypatch.setattr(cli, "display_results", fake_display_results)

    monkeypatch.setattr(
        "sys.argv",
        ["beforepush", "--target", "develop"],
    )

    cli.main()

    assert captured["target"] == "develop"
    assert captured["display_target"] == "develop"


@pytest.mark.parametrize("option", ["--verbose", "-v"])
def test_cli_verbose_option(monkeypatch, option):
    captured = {}
    monkeypatch.setattr(cli, "run_checks", lambda target: [])
    monkeypatch.setattr(
        cli,
        "display_results",
        lambda results, target, *, verbose=False: captured.update(verbose=verbose),
    )
    monkeypatch.setattr("sys.argv", ["beforepush", option])

    assert cli.main() == 0
    assert captured["verbose"] is True


def test_cli_verbose_environment_for_pre_push_hook(monkeypatch):
    captured = {}
    monkeypatch.setenv("BEFOREPUSH_VERBOSE", "1")
    monkeypatch.setattr(cli, "run_checks", lambda target: [])
    monkeypatch.setattr(
        cli,
        "display_results",
        lambda results, target, *, verbose=False: captured.update(verbose=verbose),
    )
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0
    assert captured["verbose"] is True


def test_display_results_only_shows_diagnostics_when_verbose(monkeypatch, capsys):
    monkeypatch.setattr(
        output,
        "get_diagnostics",
        lambda target: [("Repository", "/tmp/example")],
    )

    output.display_results([], "main")
    normal_output = capsys.readouterr().out
    assert "Diagnostics" not in normal_output
    assert "/tmp/example" not in normal_output

    output.display_results([], "main", verbose=True)
    verbose_output = capsys.readouterr().out
    assert "Diagnostics" in verbose_output
    assert "/tmp/example" in verbose_output


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
        lambda target: [
            CheckResult("Example", CheckStatus.PASS, "Passed."),
        ],
    )
    monkeypatch.setattr(
        cli,
        "display_results",
        lambda results, target, *, verbose=False: None,
    )
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0


def test_cli_returns_zero_when_checks_only_warn(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target: [
            CheckResult("Example", CheckStatus.WARNING, "Warning."),
        ],
    )
    monkeypatch.setattr(
        cli,
        "display_results",
        lambda results, target, *, verbose=False: None,
    )
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 0


def test_cli_returns_nonzero_when_check_fails(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target: [
            CheckResult("Example", CheckStatus.FAIL, "Failed."),
        ],
    )
    monkeypatch.setattr(
        cli,
        "display_results",
        lambda results, target, *, verbose=False: None,
    )
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
