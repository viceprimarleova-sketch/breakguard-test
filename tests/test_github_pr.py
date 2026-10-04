from pathlib import Path
import json
import subprocess

import pytest

from breakguard.github_pr import (
    changed_paths,
    ensure_clean_worktree,
    github_request,
    run,
    run_breakguard_apply,
)


def _init_repo(path: Path) -> None:
    run(["git", "init"], cwd=path)
    run(["git", "config", "user.name", "BreakGuard Test"], cwd=path)
    run(["git", "config", "user.email", "breakguard-test@example.invalid"], cwd=path)
    (path / "tracked.txt").write_text("clean\n", encoding="utf-8")
    run(["git", "add", "tracked.txt"], cwd=path)
    run(["git", "commit", "-m", "Initial"], cwd=path)


def test_run_executes_command(tmp_path: Path):
    out = run(["python", "-c", "print('ok')"], cwd=tmp_path)
    assert out == "ok"


def test_clean_worktree_guard_rejects_local_changes(tmp_path: Path):
    _init_repo(tmp_path)
    ensure_clean_worktree(tmp_path)

    (tmp_path / "tracked.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="dirty Git worktree"):
        ensure_clean_worktree(tmp_path)


def test_changed_paths_lists_only_worktree_diff(tmp_path: Path):
    _init_repo(tmp_path)
    (tmp_path / "tracked.txt").write_text("changed\n", encoding="utf-8")

    assert changed_paths(tmp_path) == ["tracked.txt"]


def test_breakguard_apply_rejects_scanner_crash(monkeypatch, tmp_path: Path):
    failed = subprocess.CompletedProcess(
        args=["breakguard"],
        returncode=2,
        stdout="",
        stderr="boom",
    )
    monkeypatch.setattr("breakguard.github_pr.subprocess.run", lambda *args, **kwargs: failed)

    with pytest.raises(RuntimeError, match="BreakGuard scan/fix failed"):
        run_breakguard_apply(tmp_path)


def test_breakguard_apply_allows_remaining_manual_findings(monkeypatch, tmp_path: Path):
    result = subprocess.CompletedProcess(
        args=["breakguard"],
        returncode=1,
        stdout="Findings: 1",
        stderr="",
    )
    monkeypatch.setattr("breakguard.github_pr.subprocess.run", lambda *args, **kwargs: result)

    assert run_breakguard_apply(tmp_path).returncode == 1


def test_github_request_serializes_payload(monkeypatch):
    seen = {}

    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b'{"html_url":"https://example.test/pr/1"}'

    def fake_urlopen(req):
        seen["method"] = req.get_method()
        seen["data"] = json.loads(req.data.decode("utf-8"))
        seen["authorization"] = req.headers["Authorization"]
        return Response()

    monkeypatch.setattr("breakguard.github_pr.request.urlopen", fake_urlopen)
    result = github_request(
        "POST",
        "https://api.github.test/repos/o/r/pulls",
        "secret-token",
        {"draft": True, "head": "fix", "base": "main"},
    )
    assert result["html_url"].endswith("/1")
    assert seen["method"] == "POST"
    assert seen["data"]["draft"] is True
    assert seen["authorization"] == "Bearer secret-token"
