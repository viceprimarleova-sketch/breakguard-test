from __future__ import annotations

from difflib import unified_diff
from pathlib import Path
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


def apply_fixes(root: Path, findings: list, dry_run: bool = False) -> list[str]:
    changed: list[str] = []

    for rel, file_findings in _group_autofix_findings(findings).items():
        path = root / rel
        with path.open(encoding="utf-8", newline="") as stream:
            original = stream.read()
        updated = _render_fixed_text(original, file_findings)

        if updated != original:
            changed.append(rel)
            if not dry_run:
                with path.open("w", encoding="utf-8", newline="") as stream:
                    stream.write(updated)

    return changed


def preview_fixes(root: Path, findings: list) -> dict[str, str]:
    previews: dict[str, str] = {}

    for rel, file_findings in _group_autofix_findings(findings).items():
        path = root / rel
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
