from pathlib import Path

from breakguard.github_pr import run


def test_run_executes_command(tmp_path: Path):
    out = run(["python", "-c", "print('ok')"], cwd=tmp_path)
    assert out == "ok"
