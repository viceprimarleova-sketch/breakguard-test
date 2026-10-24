from __future__ import annotations

import argparse
import json
import re
import sys
from importlib.resources import files
from pathlib import Path

from . import __version__
from .backups import restore_backup
from .scanner import load_rules, scan_repository
from .fixer import apply_with_backup, preview_fixes
from .reporting import make_report


def default_rules_path() -> Path:
    return Path(str(files("breakguard").joinpath("rules", "shopify_2026_10.json")))


def main() -> int:
    parser = argparse.ArgumentParser(prog="breakguard")
    parser.add_argument("repository", nargs="?", default=".")
    parser.add_argument("--rules", default=str(default_rules_path()))
    parser.add_argument("--json", action="store_true", help="Print findings as a JSON array; status goes to stderr")
    parser.add_argument("--report", type=Path, help="Write a new JSON report with coverage and limits (never overwrite)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fix-preview", action="store_true")
    group.add_argument("--apply-fixes", action="store_true")
    group.add_argument("--restore", metavar="BACKUP_ID", help="Restore a local snapshot if no later edits conflict")
    args = parser.parse_args()
    if args.fix_preview and args.json:
        parser.error("--fix-preview prints a diff; use --report for a JSON summary.")
    report_stream = None
    report_written = False
    try:
        root = Path(args.repository).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Repository must be an existing directory.")
        if args.report and (args.report.suffix.lower() != ".json" or args.report.exists()):
            raise ValueError("--report requires a new .json file; existing files are never overwritten.")
        rules = load_rules(Path(args.rules))
        if args.report:
            report_stream = args.report.open("x", encoding="utf-8")
        restored = restore_backup(root, args.restore) if args.restore else []
        result = scan_repository(root, rules)
        status_stream = sys.stderr if args.json else sys.stdout
        changed, backup_id = [], None
        mode = "restore" if args.restore else "scan"
        if args.restore:
            print(f"Restored files: {len(restored)}", file=status_stream)
        if args.fix_preview:
            mode = "preview"
            previews = preview_fixes(root, result.findings)
            for rel in sorted(previews):
                print(previews[rel], end="" if previews[rel].endswith("\n") else "\n")
            if not previews:
                print("No auto-fixable changes available.")
            print(f"Previewed files: {len(previews)}")
        if args.apply_fixes:
            mode = "apply"
            fixed = apply_with_backup(root, result.findings)
            changed, backup_id = fixed.changed, fixed.backup_id
            result = scan_repository(root, rules)
            print(f"Changed files: {len(changed)}", file=status_stream)
            if backup_id:
                print(f"Backup: {backup_id}", file=status_stream)
                print(f"Restore: breakguard <same-repository> --restore {backup_id}", file=status_stream)
        if args.report:
            report = make_report(result, rules, mode, changed, backup_id)
            report["restored_files"] = restored
            json.dump(report, report_stream, indent=2)
            report_stream.write("\n")
            report_stream.flush()
            report_written = True
        if args.json:
            print(json.dumps([f.to_dict() for f in result.findings], indent=2))
        elif not args.fix_preview:
            for f in result.findings:
                print(f"[{f.severity.upper()}] {f.file}:{f.line} {f.rule_id}")
                print(f"  {f.message}\n  Fix: {f.remediation}\n  Source: {f.source}")
                if f.review_reason:
                    print(f"  Review: {f.review_reason}")
            print(f"Findings: {len(result.findings)}")
        if not args.json:
            summary = result.summary
            print(f"Coverage: {summary.files_scanned}/{summary.files_seen} files scanned; "
                  f"{summary.embedded_documents_scanned} embedded documents; "
                  f"{summary.embedded_documents_skipped} embedded documents skipped.")
            print("Limited rule coverage; no findings does not certify Shopify API compatibility.")
        return 1 if result.findings else 0
    except (OSError, ValueError, TypeError, KeyError, re.error) as exc:
        print(f"breakguard: error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"breakguard: internal error ({type(exc).__name__}); no successful scan result produced.", file=sys.stderr)
        return 2
    finally:
        if report_stream:
            try:
                report_stream.close()
                if not report_written:
                    args.report.unlink(missing_ok=True)
            except OSError as exc:
                print(f"breakguard: report cleanup error: {exc}", file=sys.stderr)
                return 2


if __name__ == "__main__":
    raise SystemExit(main())
