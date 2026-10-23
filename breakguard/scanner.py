from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from .graphql_edits import GRAPHQL_ACTIONS, matches_action, plan_edits, query_fields


@dataclass
class Finding:
    rule_id: str
    severity: str
    file: str
    line: int
    message: str
    remediation: str
    source: str
    auto_fix: str | None

    def to_dict(self):
        return asdict(self)


def load_rules(rule_file: Path) -> list[dict]:
    return json.loads(rule_file.read_text(encoding="utf-8"))["rules"]


def iter_files(root: Path) -> Iterable[Path]:
    ignored = {".git", "node_modules", ".venv", "venv", "__pycache__"}
    for p in root.rglob("*"):
        if p.is_file() and not any(part in ignored for part in p.parts):
            yield p


def _rule_applies_to_path(path: Path, rule: dict) -> bool:
    if any(part in rule.get("exclude_path_parts", []) for part in path.parts):
        return False
    if rule.get("exclude_test_files") and re.search(r"(?:^test_|_test\.|\.(?:test|spec)\.)", path.name):
        return False
    extensions = rule.get("extensions")
    if not extensions:
        return True
    allowed = {ext.lower() for ext in extensions}
    return path.suffix.lower() in allowed


def _context_matches(lines: list[str], index: int, rule: dict) -> bool:
    context_before = rule.get("context_before")
    if context_before:
        max_lines = int(rule.get("context_max_lines", 12))
        start = max(0, index - max_lines)
        return any(context_before in candidate for candidate in lines[start:index + 1])

    context = rule.get("context")
    if context:
        return context in "\n".join(lines)

    return True


def scan(root: Path, rules: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = text.splitlines()
        rel = str(path.relative_to(root))
        for rule in rules:
            if not _rule_applies_to_path(Path(rel), rule):
                continue
            pattern = rule["pattern"]
            action = rule.get("auto_fix")
            if action in GRAPHQL_ACTIONS:
                fields = query_fields(text)
                if fields is not None:
                    matched = [field for field in fields if matches_action(field, action)]
                    edits = plan_edits(text, {(field.line, action) for field in matched}, fields)
                    matched_counts = Counter(field.line for field in matched)
                    edit_counts = Counter(edit.line for edit in edits)
                    safe_lines = {line for line, count in matched_counts.items()
                                  if edit_counts[line] == count}
                    for field in matched:
                        findings.append(Finding(
                            rule_id=rule["id"], severity=rule["severity"], file=rel,
                            line=field.line, message=rule["message"],
                            remediation=rule["remediation"], source=rule["source"],
                            auto_fix=action if field.line in safe_lines else None,
                        ))
                    continue
            for index, line in enumerate(lines):
                if rule.get("regex"):
                    if line.lstrip().startswith(("#", "//", "*", "/*")):
                        continue
                    if not re.search(rule["regex"], line):
                        continue
                elif pattern not in line:
                    continue
                if not _context_matches(lines, index, rule):
                    continue
                if action in GRAPHQL_ACTIONS and line.lstrip().startswith("#"):
                    continue
                findings.append(Finding(
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    file=rel,
                    line=index + 1,
                    message=("Potential match in an unparseable GraphQL document; confirm manually. "
                             + rule["message"]) if action in GRAPHQL_ACTIONS else rule["message"],
                    remediation=rule["remediation"],
                    source=rule["source"],
                    auto_fix=None if action in GRAPHQL_ACTIONS else action,
                ))
    return findings
