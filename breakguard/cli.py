from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path

from . import __version__
from .scanner import load_rules, scan
from .fixer import apply_fixes, preview_fixes


def default_rules_path() -> Path:
    return Path(str(files("breakguard").joinpath("rules", "shopify_2026_10.json")))


def main() -> int:
    parser = argparse.ArgumentParser(prog="breakguard")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--rules", default=str(default_rules_path()))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    fix_group = parser.add_mutually_exclusive_group()
    fix_group.add_argument("--fix-preview", action="store_true")
    fix_group.add_argument("--apply-fixes", action="store_true")
    args = parser.parse_args()

    root = Path(args.repository).resolve()
    rules = load_rules(Path(args.rules))
    findings = scan(root, rules)

    if args.fix_preview:
        previews = preview_fixes(root, findings)
        if previews:
            for rel in sorted(previews):
                print(previews[rel], end="" if previews[rel].endswith("\n") else "\n")
        else:
            print("No auto-fixable changes available.")
        print(f"Previewed files: {len(previews)}")
        return 1 if findings else 0

    if args.apply_fixes:
        changed = apply_fixes(root, findings)
        findings = scan(root, rules)
        print(f"Changed files: {len(changed)}")

    if args.json:
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        for f in findings:
            print(f"[{f.severity.upper()}] {f.file}:{f.line} {f.rule_id}")
            print(f"  {f.message}")
            print(f"  Fix: {f.remediation}")
            print(f"  Source: {f.source}")
        print(f"Findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
