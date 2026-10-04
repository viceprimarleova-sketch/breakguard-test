from __future__ import annotations

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


def apply_fixes(root: Path, findings: list, dry_run: bool = False) -> list[str]:
    changed: list[str] = []
    by_file: dict[str, list] = {}
    for f in findings:
        if f.auto_fix:
            by_file.setdefault(f.file, []).append(f)

    for rel, file_findings in by_file.items():
        path = root / rel
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines()

        for f in sorted(file_findings, key=lambda x: x.line, reverse=True):
            idx = f.line - 1
            if f.auto_fix == "remove_graphql_field_block" and "lastIncompleteCheckout" in lines[idx]:
                lines = _remove_graphql_field_block(lines, idx)
            elif f.auto_fix == "replace_price_rule" and "priceRule" in lines[idx]:
                indent = lines[idx][:len(lines[idx]) - len(lines[idx].lstrip())]
                lines[idx:idx+1] = [f"{indent}discountTitle", f"{indent}discountCode"]

        updated = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
        if updated != original:
            changed.append(rel)
            if not dry_run:
                path.write_text(updated, encoding="utf-8")
    return changed
