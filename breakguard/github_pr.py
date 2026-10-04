from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib import request, error


def run(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()


def github_request(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        method=method,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "BreakGuard-V0.1",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare BreakGuard fixes and optionally open a Draft PR")
    parser.add_argument("--repo", help="GitHub repository in owner/name form")
    parser.add_argument("--base", default="main")
    parser.add_argument("--branch", default="breakguard/auto-fix")
    parser.add_argument("--verify-cmd", default="python -m pytest -q")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path.cwd()
    run(["git", "checkout", "-B", args.branch, args.base], cwd=root)

    scan = subprocess.run(
        [sys.executable, "-m", "breakguard.cli", ".", "--apply-fixes"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    print(scan.stdout)
    if scan.stderr:
        print(scan.stderr, file=sys.stderr)

    changed = run(["git", "status", "--porcelain"], cwd=root)
    if not changed:
        print("No auto-fixable changes produced.")
        return 0

    verify = subprocess.run(args.verify_cmd, cwd=root, shell=True)
    if verify.returncode != 0:
        print("Verification failed; refusing to continue.", file=sys.stderr)
        return verify.returncode

    run(["git", "add", "-A"], cwd=root)
    run(["git", "commit", "-m", "BreakGuard: apply safe deprecation fixes"], cwd=root)

    if args.dry_run:
        print(f"DRY RUN: prepared branch {args.branch} from {args.base}")
        return 0

    if not args.repo:
        print("--repo is required when not using --dry-run", file=sys.stderr)
        return 2

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is required when not using --dry-run", file=sys.stderr)
        return 2

    run(["git", "push", "origin", f"HEAD:{args.branch}", "--force-with-lease"], cwd=root)

    pr = github_request(
        "POST",
        f"https://api.github.com/repos/{args.repo}/pulls",
        token,
        {
            "title": "BreakGuard: apply safe Shopify deprecation fixes",
            "head": args.branch,
            "base": args.base,
            "draft": True,
            "body": (
                "Generated automatically by BreakGuard V0.1.\n\n"
                "Only conservative auto-fixes were applied.\n"
                "Verification passed before this Draft PR was created.\n"
                "Manual-only findings remain unchanged."
            ),
        },
    )
    print(pr.get("html_url", "Draft PR created"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
