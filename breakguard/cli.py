from __future__ import annotations

import argparse
import json
from pathlib import Path

from .scanner import load_rules, scan
from .fixer import apply_fixes


def main() -> int:
    parser = argparse.ArgumentParser(prog="breakguard")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--rules", default=str(Path(__file__).resolve().parents[1] / "rules" / "shopify_2026_10.json"))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--apply-fixes", action="store_true")
    args = parser.parse_args()

    root = Path(args.repository).resolve()
    rules = load_rules(Path(args.rules))
    findings = scan(root, rules)

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
