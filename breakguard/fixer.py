from __future__ import annotations

from difflib import unified_diff
from pathlib import Path
from dataclasses import dataclass
from .backups import safe_path, save_and_apply
from .graphql_edits import GRAPHQL_ACTIONS, plan_edits, render_edits


def _group_autofix_findings(findings: list) -> dict[str, list]:
    by_file: dict[str, list] = {}
    for finding in findings:
        if finding.auto_fix:
            by_file.setdefault(finding.file, []).append(finding)
    return by_file


def _render_fixed_text(original: str, file_findings: list) -> str:
    requested = {(f.line, f.auto_fix) for f in file_findings if f.auto_fix in GRAPHQL_ACTIONS}
    return render_edits(original, plan_edits(original, requested))


@dataclass
class FixResult:
    changed: list[str]
    backup_id: str | None


def apply_with_backup(root: Path, findings: list, dry_run: bool = False) -> FixResult:
    root = root.resolve(strict=True)
    changes = {}
    for rel, file_findings in _group_autofix_findings(findings).items():
        path = safe_path(root, rel)
        original_bytes = path.read_bytes()
        original = original_bytes.decode("utf-8")
        updated = _render_fixed_text(original, file_findings)
        if updated != original:
            changes[rel] = (original_bytes, updated.encode("utf-8"))
    backup_id = save_and_apply(root, changes) if changes and not dry_run else None
    return FixResult(list(changes), backup_id)


def apply_fixes(root: Path, findings: list, dry_run: bool = False) -> list[str]:
    return apply_with_backup(root, findings, dry_run).changed


def preview_fixes(root: Path, findings: list) -> dict[str, str]:
    previews: dict[str, str] = {}

    for rel, file_findings in _group_autofix_findings(findings).items():
        path = safe_path(root.resolve(strict=True), rel)
        with path.open(encoding="utf-8", newline="") as stream:
            original = stream.read()
        updated = _render_fixed_text(original, file_findings)

        if updated == original:
            continue

        diff = unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        )
        previews[rel] = "".join(diff)

    return previews
