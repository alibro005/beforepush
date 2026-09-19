import subprocess

import git
from checks import CheckStatus, check_large_staged_files


def _git(*args):
    subprocess.run(["git", *args], check=True, capture_output=True)


def _init_repository(path, monkeypatch):
    _git("init", "--initial-branch=main", str(path))
    monkeypatch.chdir(path)
    _git("config", "user.name", "Test User")
    _git("config", "user.email", "test@example.com")
    (path / "existing.bin").write_bytes(b"x" * 4096)
    _git("add", "existing.bin")
    _git("commit", "-m", "Initial commit")


def test_large_file_check_only_reports_new_staged_files(tmp_path, monkeypatch):
    _init_repository(tmp_path, monkeypatch)

    # A modified, already tracked file must not be reported, even when large.
    (tmp_path / "existing.bin").write_bytes(b"x" * 8192)
    _git("add", "existing.bin")

    (tmp_path / "below.bin").write_bytes(b"x" * 512)
    (tmp_path / "exact.bin").write_bytes(b"x" * 1024)
    (tmp_path / "large-one.bin").write_bytes(b"x" * 2048)
    (tmp_path / "large-two.bin").write_bytes(b"x" * 4096)
    _git("add", "below.bin", "exact.bin", "large-one.bin", "large-two.bin")

    result = check_large_staged_files(1024)

    assert result.status == CheckStatus.WARNING
    assert "large-one.bin" in result.message
    assert "large-two.bin" in result.message
    assert "existing.bin" not in result.message
    assert "below.bin" not in result.message
    assert "exact.bin" not in result.message
    assert len(git.get_staged_added_files()) == 4


def test_unstaged_untracked_large_file_is_not_checked(tmp_path, monkeypatch):
    _init_repository(tmp_path, monkeypatch)
    (tmp_path / "untracked.bin").write_bytes(b"x" * 2048)

    result = check_large_staged_files(1024)

    assert result.status == CheckStatus.PASS
    assert "untracked.bin" not in result.message


def test_staged_blob_size_is_used_if_working_file_changes(tmp_path, monkeypatch):
    _init_repository(tmp_path, monkeypatch)
    staged_file = tmp_path / "staged.bin"
    staged_file.write_bytes(b"x" * 2048)
    _git("add", "staged.bin")
    staged_file.write_bytes(b"x")

    result = check_large_staged_files(1024)

    assert result.status == CheckStatus.WARNING
    assert "staged.bin (2.0 KB)" in result.message
