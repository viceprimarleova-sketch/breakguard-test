from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare BreakGuard fixes on a dedicated branch")
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

    print("Branch prepared locally. Push/PR creation is intentionally separate in V0.1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
