import cli
from checks import CheckResult, CheckStatus


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

    exit_code = cli.main()

    assert captured["target"] == "main"
    assert captured["display_target"] == "main"
    assert captured["results"] == []
    assert exit_code == 0


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


def test_cli_returns_zero_when_checks_pass(monkeypatch):
    monkeypatch.setattr(
        cli,
        "run_checks",
        lambda target: [
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
        lambda target: [
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
        lambda target: [
            CheckResult("Example", CheckStatus.FAIL, "Failed."),
        ],
    )
    monkeypatch.setattr(cli, "display_results", lambda results, target: None)
    monkeypatch.setattr("sys.argv", ["beforepush"])

    assert cli.main() == 1
