import subprocess

import pytest

import cli


def test_cli_uses_main_by_default(monkeypatch):
    captured = {}

    def fake_run_checks(target):
        captured["target"] = target
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

    cli.main()

    assert captured["target"] == "main"
    assert captured["display_target"] == "main"
    assert captured["results"] == []


def test_cli_accepts_custom_target(monkeypatch):
    captured = {}

    def fake_run_checks(target):
        captured["target"] = target
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
    assert captured["display_target"] == "develop"


@pytest.mark.parametrize("branch", ["main", "feature/test"])
def test_cli_without_commits(tmp_path, monkeypatch, capsys, branch):
    subprocess.run(
        ["git", "init", "--initial-branch", branch, str(tmp_path)],
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["beforepush"])

    cli.main()

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
            "-c", "user.name=Test User",
            "-c", "user.email=test@example.com",
            "-c", "commit.gpgsign=false",
            "commit", "--allow-empty", "-m", "Initial commit",
        ],
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr("sys.argv", ["beforepush"])

    cli.main()

    output = capsys.readouterr().out
    assert "no commits" not in output
    assert "Working tree is clean." in output
    assert "No upstream branch configured." in output
    assert "Currently on target branch 'main'." in output
