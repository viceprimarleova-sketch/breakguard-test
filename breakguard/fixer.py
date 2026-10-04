from __future__ import annotations

from difflib import unified_diff
from pathlib import Path


def _remove_graphql_field_block(lines: list[str], index: int) -> list[str]:
    line = lines[index]
    if "{" not in line:
        return lines[:index] + lines[index + 1:]
    depth = line.count("{") - line.count("}")
    j = index + 1
    while j < len(lines) and depth > 0:
        depth += lines[j].count("{") - lines[j].count("}")
        j += 1
    return lines[:index] + lines[j:]


def _group_autofix_findings(findings: list) -> dict[str, list]:
    by_file: dict[str, list] = {}
    for finding in findings:
        if finding.auto_fix:
            by_file.setdefault(finding.file, []).append(finding)
    return by_file


def _render_fixed_text(original: str, file_findings: list) -> str:
    lines = original.splitlines()

    for finding in sorted(file_findings, key=lambda item: item.line, reverse=True):
        idx = finding.line - 1
        if idx < 0 or idx >= len(lines):
            continue
        if finding.auto_fix == "remove_graphql_field_block" and "lastIncompleteCheckout" in lines[idx]:
            lines = _remove_graphql_field_block(lines, idx)
        elif finding.auto_fix == "replace_price_rule" and "priceRule" in lines[idx]:
            indent = lines[idx][:len(lines[idx]) - len(lines[idx].lstrip())]
            lines[idx:idx + 1] = [f"{indent}discountTitle", f"{indent}discountCode"]

    return "\n".join(lines) + ("\n" if original.endswith("\n") else "")


def apply_fixes(root: Path, findings: list, dry_run: bool = False) -> list[str]:
    changed: list[str] = []

    for rel, file_findings in _group_autofix_findings(findings).items():
        path = root / rel
        original = path.read_text(encoding="utf-8")
        updated = _render_fixed_text(original, file_findings)

        if updated != original:
            changed.append(rel)
            if not dry_run:
                path.write_text(updated, encoding="utf-8")

    return changed


def preview_fixes(root: Path, findings: list) -> dict[str, str]:
    previews: dict[str, str] = {}

    for rel, file_findings in _group_autofix_findings(findings).items():
        path = root / rel
        original = path.read_text(encoding="utf-8")
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
