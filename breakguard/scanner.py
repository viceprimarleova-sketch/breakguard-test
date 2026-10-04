from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


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
    extensions = rule.get("extensions")
    if not extensions:
        return True
    allowed = {ext.lower() for ext in extensions}
    return path.suffix.lower() in allowed


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
            if not _rule_applies_to_path(path, rule):
                continue
            pattern = rule["pattern"]
            context = rule.get("context")
            for i, line in enumerate(lines, start=1):
                if pattern not in line:
                    continue
                if context and context not in text:
                    continue
                findings.append(Finding(
                    rule_id=rule["id"],
                    severity=rule["severity"],
                    file=rel,
                    line=i,
                    message=rule["message"],
                    remediation=rule["remediation"],
                    source=rule["source"],
                    auto_fix=rule.get("auto_fix"),
                ))
    return findings
