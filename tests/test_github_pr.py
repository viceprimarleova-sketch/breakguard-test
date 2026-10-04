from pathlib import Path
import json

from breakguard.github_pr import run, github_request


def test_run_executes_command(tmp_path: Path):
    out = run(["python", "-c", "print('ok')"], cwd=tmp_path)
    assert out == "ok"


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
